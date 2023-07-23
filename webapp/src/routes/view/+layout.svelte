<script lang="ts">
  import { onMount } from "svelte";
  import { fade } from "svelte/transition";
  import { page } from "$app/stores";

  import Prompt from "$lib/components/ChatPrompt.svelte";
  import Response from "$lib/components/ChatResponse.svelte";
  import PromptSummary from "$lib/components/ChatPromptSummary.svelte";

  let prompt_list: Data_ChatPrompt[] = [];
  let projects: Array<string> = [];
  let project: string;

  onMount(() => {
    console.log("onMount");
    // fetch("http://localhost:8000/projects/")
    //   .then((res) => res.json())
    //   .then((j) => {
    //     projects = j;
    //   });

    fetch("http://localhost:8000/prompts/?" + new URLSearchParams({ project: "default" }))
      .then((res) => res.json())
      .then((j) => {
        prompt_list = j.sort((a: Data_ChatPrompt, b: Data_ChatPrompt) => {
          return b.id - a.id;
        });
      });

    const eventSource = new EventSource(
      "http://localhost:8000/updates/?" + new URLSearchParams({ project: "default" })
    );
    eventSource.onerror = (err) => {
      console.log("err", err);
    };

    eventSource.addEventListener("create_prompt", (event) => {
      const data = JSON.parse(event.data);
      prompt_list = [data, ...prompt_list];
    });

    eventSource.addEventListener("update_prompt", (event) => {
      const data = JSON.parse(event.data);
      const index = prompt_list.findIndex((p) => p.id == data.id);

      if (index !== -1) {
        prompt_list[index] = data;
        prompt_list = prompt_list; // force update
      } else {
        prompt_list = [data, ...prompt_list];
      }
    });

    eventSource.addEventListener("delete_prompt", (event) => {
      const data = JSON.parse(event.data);
      prompt_list = prompt_list.filter((p) => p.id != data.id);
    });

    eventSource.addEventListener("create_response", (event) => {
      const data = JSON.parse(event.data);
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        prompt.responses = [data, ...prompt.responses];
        prompt_list = prompt_list; // force update
      }
    });

    eventSource.addEventListener("update_response", (event) => {
      const data = JSON.parse(event.data);
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        const index = prompt.responses.findIndex((r) => r.id == data.id);
        if (index !== -1) {
          prompt.responses[index] = data;
        } else {
          prompt.responses = [data, ...prompt.responses];
        }
        prompt_list = prompt_list; // force update
      }
    });

    eventSource.addEventListener("delete_response", (event) => {
      const data = JSON.parse(event.data);
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        prompt.responses = prompt.responses.filter((r) => r.id != data.id);
        prompt_list = prompt_list; // force update
      }
    });

    eventSource.addEventListener("stream_in", (event) => {
      const data = JSON.parse(event.data);
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        const response = prompt.responses.find((r) => r.id == data.id);
        if (response) {
          response.response.content += data.message;
          prompt_list = prompt_list; // force update
        }
      }
    });
  });

  // $:

  $: view_id = parseInt($page.params.id);
  $: selected_prompt = prompt_list.find((p) => p.id == view_id);
</script>

<!-- <pre>{JSON.stringify($page,null,2)}</pre> -->

<div class="flex flex-col h-screen" data-sveltekit-preload-data="off">
  <div class="flex overflow-hidden grow">
    <div class="overflow-y-scroll shrink-0 w-52 max-w-md">
      {#each prompt_list as prompt}
        {@const id = prompt.id}
        {@const target = "/view/" + (id == view_id ? "" : id)}
        <a href={target}>
          <PromptSummary class="max-w-sm" {prompt} active={id == view_id} />
        </a>
      {/each}
    </div>
    {#if view_id}
      {#if selected_prompt}
        <div class="flex grow" transition:fade>
          <div class="flex flex-col md:flex-row flex-grow">
            <Prompt class="md:w-1/2" prompt={selected_prompt} />
            <div class="md:w-1/2">
              {#if selected_prompt.responses}
                {#each selected_prompt.responses as response}
                  <Response {response} />
                {/each}
              {/if}
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>
</div>
