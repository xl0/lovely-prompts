<script lang="ts">
  import { onMount } from "svelte";

  import Bubble from "$lib/components/Bubble.svelte";
  import Message from "$lib/components/ChatMessage.svelte";
  import Prompt from "$lib/components/ChatPrompt.svelte";
  import Response from "$lib/components/ChatResponse.svelte";
  import PromptSummary from "$lib/components/ChatPromptSummary.svelte";

  let message: ChatMessage = {
    role: "User",
    content:
      "Lorem ipsum dolor sit amet consectetur, adipisicing elit. Iste fuga reiciendis ut nulla consectetur recusandae numquam enim inventore quod minus eligendi, aut est? Assumenda reiciendis quis sit eum magni doloremque. Libero officiis dolores cupiditate. Inventore facere rerum itaque incidunt dolore totam mollitia dolorem eum, ratione repudiandae. Iusto tenetur ducimus nam illo magnam cupiditate sapiente facilis nobis. Illo mollitia porro deserunt vero, aliquid exercitationem beatae nobis sunt quia odio atque nihil deleniti animi molestias ratione, accusantium minima impedit reiciendis amet natus illum ipsum nemo. Nobis itaque, hic asperiores quisquam non quam ex praesentium minima a quae libero laudantium numquam, maiores minus!",
    title: " ddddddddddddddddddfsd",
    comment: "comment",
  };


  let response: ChatResponse = {
    id: 1,
    prompt_id: 2,
    response: { role: "Assistant", content: message.content?.toUpperCase(), comment: "sdfdsfsdfsd" },
    tok_in: 10,
    // tok_out: 20,
    tok_max: 30,
    provider: "OpenAI",
    model: "gpt-3.5-turbo",
    temperature: 0.8,
    // title: "response title",
    comment: "response comment",
    meta: {
      Hello: "World",
      meta: "data",
    },
    created: "2023-07-20T12:10:45",
    updated: "2023-07-20T12:10:45"
  };

  let prompt: ChatPrompt = {
    id: 2,
    messages: [message, message],
    // title: "titlesdfdsfds fs ddf sdfsd sd sd f",
    comment: "comment",
    created: "2023-07-20T12:10:45",
    updated: "2023-07-20T12:10:45",
    responses: [response, response]
  };

  let prompt_list: ChatPrompt[]

  // onMount(() => {
  //   fetch("http://localhost:8000/prompts/")
  //     .then((res) => res.json())
  //     .then((json) => {
  //       prompt_list = json;
  //     });
  // });


</script>

<!-- <div class="flex flex-col md:flex-row">
  <Prompt class="md:w-1/2" {prompt} />
  <Response class="md:w-1/2" {response} />
</div> -->

<div class="flex flex-col h-screen" data-sveltekit-preload-data="off">

<div class="flex overflow-hidden grow">
  <div class="overflow-y-scroll shrink-0 w-52 max-w-md">
    <PromptSummary class="max-w-sm" {prompt} />
  </div>
</div>
</div>