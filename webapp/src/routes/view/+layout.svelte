<script lang="ts">
  import { onMount } from "svelte";
  import { fade } from "svelte/transition";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";

  import Prompt from "$lib/components/ChatPrompt.svelte";
  import Response from "$lib/components/ChatResponse.svelte";
  import PromptSummary from "$lib/components/ChatPromptSummary.svelte";

  import { UpdateEvents } from "$lib";
    import { PUBLIC_SERVER_URL } from "$env/static/public";

  let prompt_list: Data_LLMPrompt[] = [];
  let projects: Array<string> = [];
  let project: string;

  onMount(() => {
    console.log("onMount");
    // fetch("http://localhost:8000/projects/")
    //   .then((res) => res.json())
    //   .then((j) => {
    //     projects = j;
    //   });



    fetch(`${PUBLIC_SERVER_URL}/chat_prompts/?` + new URLSearchParams({ project: "default" }))
      .then((res) => res.json())
      .then((j) => {
        prompt_list = j;

        // .sort((a: Data_LLMPrompt, b: Data_LLMPrompt) => {
        //   return b.id - a.id;
        // });
      });

    const eventSource = new EventSource(
      `${PUBLIC_SERVER_URL}/updates/?` + new URLSearchParams({ project: "default" })
    );
    eventSource.onerror = (err) => {
      console.log("err", err);
    };

    eventSource.addEventListener(UpdateEvents.NEW_CHAT_PROMPT, (event) => {
      const data = JSON.parse(event.data);
      prompt_list = [data, ...prompt_list];
      goto("/view/" + data.id);
    });

    eventSource.addEventListener(UpdateEvents.UPDATE_CHAT_PROMPT, (event) => {
      const data = JSON.parse(event.data);
      const index = prompt_list.findIndex((p) => p.id == data.id);

      if (index !== -1) {
        prompt_list[index] = data;
        prompt_list = prompt_list; // force update
      } else {
        prompt_list = [data, ...prompt_list];
      }
    });

    eventSource.addEventListener(UpdateEvents.DELETE_CHAT_PROMPT, (event) => {
      const data = JSON.parse(event.data);
      prompt_list = prompt_list.filter((p) => p.id != data.id);
    });
    eventSource.addEventListener(UpdateEvents.NEW_CHAT_RESPONSE, (event) => {
      const data = JSON.parse(event.data);
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        prompt.responses = [data, ...(prompt.responses ?? [])];
        prompt_list = prompt_list; // force update
      }
    });

    eventSource.addEventListener(UpdateEvents.UPDATE_CHAT_RESPONSE, (event) => {
      const data = JSON.parse(event.data);
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        prompt.responses = prompt.responses ?? [];
        const index = prompt.responses.findIndex((r) => r.id == data.id);
        if (index !== -1) {
          prompt.responses[index] = data;
        } else {
          prompt.responses = [data, ...prompt.responses];
        }
        prompt_list = prompt_list; // force update
      }
    });

    eventSource.addEventListener(UpdateEvents.DELETE_CHAT_RESPONSE, (event) => {
      const data = JSON.parse(event.data);
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        prompt.responses = prompt.responses ?? [];
        prompt.responses = prompt.responses.filter((r) => r.id != data.id);
        prompt_list = prompt_list; // force update
      }
    });

    eventSource.addEventListener(UpdateEvents.STREAM_CHAT_RESPONSE, (event) => {
      const data = JSON.parse(event.data) as WSMessage;
      const prompt = prompt_list.find((p) => p.id == data.prompt_id);
      if (prompt) {
        prompt.responses = prompt.responses ?? [];
        const response = prompt.responses?.find((r) => r.id == data.id);
        if (response) {
          if (data.action == "replace") {
            response[data.key] = data.value;
          } else if (data.action == "append") {
            response[data.key] = (response[data.key] ?? "") + data.value;
          } else if (data.action == "delete") {
            delete response[data.key];
          }
          prompt_list = prompt_list; // force update
        }
      }
    });
  });

  // $:

  $: view_id = $page.params.id;
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
          {#if selected_prompt?.responses && selected_prompt.responses.length > 1}
            <div class="flex flex-wrap md:flex-col flex-grow">
              <Prompt class="" prompt={selected_prompt} />
              <div class="flex flex-wrap justify-center">
                {#each selected_prompt.responses as response}
                  <Response {response} />
                {/each}
              </div>
            </div>
          {:else if selected_prompt?.responses && selected_prompt?.responses.length == 1}
            {@const response = selected_prompt.responses[0]}
            <div class="flex flex-col grow lg:flex-row">
              <Prompt class="lg:w-1/2" prompt={selected_prompt} />
              <Response class="lg:w-1/2" {response} />
            </div>
          {:else}
            <div class="flex flex-col grow lg:flex-row">
              <Prompt class="lg:w-1/2" prompt={selected_prompt} />
            </div>
          {/if}
        </div>
      {/if}
    {/if}
  </div>
</div>

<slot />
