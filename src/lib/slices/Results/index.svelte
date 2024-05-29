<script>
	import Bounded from "$lib/components/Bounded.svelte";
	import GradientBack from "$lib/components/Gradient_back.svelte";
	import { PrismicImage, PrismicRichText } from "@prismicio/svelte";
	// import { text } from "@sveltejs/kit";
	import clsx from "clsx";
	import { onMount } from 'svelte';

	/** @type {import("@prismicio/client").Content.ResultsSlice} */
	export let slice;

	let emotion = {};

  async function fetchData() {
    try {
      const response = await fetch('http://127.0.0.1:5000/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: 'value' }) // Adjust as necessary for your API
      });
      const result = await response.json();
      emotion = result.emotion.toUpperCase(); // Assuming the data is in the 'data' property of the response
			console.log(emotion, "ffff")
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }

  onMount(() => {
    fetchData();
  });

	function logValues(itemEmotName, dataEmotion) {
    console.log('item.emot_name:', itemEmotName[0].text);
    console.log('data.emotion:', dataEmotion);
    return ''; // This ensures nothing is rendered by the {@html} tag
  }
			
</script>

<Bounded data-slice-type={slice.slice_type} data-slice-variation={slice.variation}>
	<div class=" text-container mt-6 relative z-[100] text-center ">
		<h1  class="text-center text-balance text-5xl font-medium text-black md:text-7xl">
			<PrismicRichText field={slice.primary.emotion} />
		</h1>
		
		<div class="mx-auto grid mt-36 justify-center max-w-[10rem] gap-8 grid-rows-[auto_auto_auto] md:grid-cols-2  md:gap-10 ">
			
			{#each slice.items as item}
				{#if item.emot_name[0].text == emotion}
					<div class={clsx("glass-container row-span-2 text-center grid grid-rows-subgrid gap-4 rounded-lg bg-gray-600/40 p-4 before:bg-gray-100/10W md:col-span-2")}>
						<PrismicImage field={item.emo_img} class="max-h-50 mx-auto" />
						<h3 class="text-md text-white">
							<PrismicRichText field={item.emot_name} />
						</h3>
					</div>
				{/if}
			{@html logValues(item.emot_name, emotion)} 
			{/each}
		</div>
	</div>
	<GradientBack/>
</Bounded>
