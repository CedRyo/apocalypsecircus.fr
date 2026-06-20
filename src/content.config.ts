import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const sections = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/sections' }),
  schema: z.object({
    title: z.string(),
    sectionNumber: z.number(),
    description: z.string(),
    slug: z.string(),
    // Highwire Press metadata for Google Scholar
    citationTitle: z.string().optional(),
    citationAuthor: z.string().optional(),
    citationPublicationDate: z.string().optional(),
    citationJournalTitle: z.string().optional(),
    citationPublicUrl: z.string().optional(),
    citationPdfUrl: z.string().optional(),
    citationLanguage: z.string().optional(),
  }),
});

export const collections = { sections };
