import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const sections = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/sections' }),
  schema: z.object({
    title: z.string(),
    sectionNumber: z.number(),
    description: z.string(),
    slug: z.string(),
  }),
});

export const collections = { sections };
