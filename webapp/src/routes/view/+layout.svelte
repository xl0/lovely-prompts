<script lang="ts">
  import { onMount } from "svelte";
  import { fade } from "svelte/transition";
  import { page } from "$app/stores";

  import Prompt from "$lib/components/ChatPrompt.svelte";
  import Response from "$lib/components/ChatResponse.svelte";
  import PromptSummary from "$lib/components/ChatPromptSummary.svelte";

  let prompt_list: Data_ChatPrompt[] = [];

  onMount(() => {
    console.log("onMount");
    fetch("http://localhost:8000/prompts/")
      .then((res) => res.json())
      .then((j) => {
        prompt_list = j.sort((a: Data_ChatPrompt, b: Data_ChatPrompt) => {
          return b.id - a.id;
        });
      });
  });

$: view_id = parseInt($page.params.id);
$: selected_prompt = prompt_list.find((p) => p.id == view_id)
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
