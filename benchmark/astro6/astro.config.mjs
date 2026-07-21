import starlight from '@astrojs/starlight'
import { defineConfig } from 'astro/config'

export default defineConfig({
  site: 'https://filed.fyi',
  integrations: [
    starlight({
      title: 'Filed & Forgotten',
      description: 'Archive surface for collection-backed records.',
      disable404Route: true,
      components: {
        MarkdownContent: './src/components/starlight/MarkdownContent.astro',
      },
      sidebar: [
        {
          label: 'Aphorisms',
          items: [{ autogenerate: { directory: 'aphorisms' } }]
        },
        {
          label: 'Mascots',
          items: [{ autogenerate: { directory: 'mascots' } }]
        },
        {
          label: 'Lorelog',
          items: [{ autogenerate: { directory: 'lorelog' } }]
        },
        {
          label: 'Limericks',
          items: [{ autogenerate: { directory: 'limericks' } }]
        },
        {
          label: 'Haikus',
          items: [{ autogenerate: { directory: 'haikus' } }]
        }
      ]
    })
  ]
})
