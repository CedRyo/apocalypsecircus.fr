#!/usr/bin/env python3
"""Convert SEO HTML chapters to MDX files for the Astro project."""

import os
import re

HTML_BASE = r"C:\Users\Shadow\Documents\Apocalypse_Circus\SEO_html"
MDX_BASE  = r"C:\Users\Shadow\apocalypsecircus.fr\src\content\sections"

# (folder_name, mdx_filename_slug, sectionNumber)
SECTIONS = [
    ("section_1",  "ouverture",    0),
    ("section_2",  "section-i",    1),
    ("section_3",  "section-ii",   2),
    ("section_4",  "section-iii",  3),
    ("section_5",  "section-iv",   4),
    ("section_6",  "section-v",    5),
    ("section_7",  "section-vi",   6),
    ("section_8",  "section-vii",  7),
    ("section_9",  "section-viii", 8),
    ("section_10", "section-ix",   9),
    ("section_11", "section-xi",   11),
]

TITLES = {
    "ouverture":    "Ouverture",
    "section-i":    "Machination, expulsion, dedans",
    "section-ii":   "Anatomie d'une chute, une faille ontologique",
    "section-iii":  "Peur de manquer et mauvais infini",
    "section-iv":   "Géométrie des Noms et acte de lecture",
    "section-v":    "Psychogonie, rupture d'Iblis, genèse de l'âme",
    "section-vi":   "Écart dynamique et algèbre de la rotation (K-L-M)",
    "section-vii":  "Structure du yaqîn et ouverture des causes",
    "section-viii": "Méthode en déploiement et opérateur du nom face à la loi du chiffre",
    "section-ix":   "Point d'hérésie et reversement de l'obstacle théologique",
    "section-xi":   "Le dire ne sert à rien",
}

DESCRIPTIONS = {
    "ouverture":    "Révélation, apocalypse comme initiation, et grammaire de l'être — le rideau se lève sur l'Apocalypse Circus.",
    "section-i":    "La machination comme mécanique sans sujet : la raison instrumentale, l'expulsion du dedans, et la capture de la parole.",
    "section-ii":   "Anatomie de la chute d'Adam : la brèche ontologique, l'aspiration infinie, et la matrice du mal.",
    "section-iii":  "La peur de manquer comme moteur adamique, le mauvais infini, et la clé herméneutique du texte révélé.",
    "section-iv":   "La géométrie des Noms, la réponse divine, le don des Kalimât et la rotation initiatique K-L-M.",
    "section-v":    "Psychogonie : les trois moments de la formation de l'âme, la fracture d'Iblis et la transmission de la peur.",
    "section-vi":   "L'écart entre l'acte et le Nom, les trois prépositions du Mal, et la rotation K-L-M comme force inverse.",
    "section-vii":  "Structure du yaqîn soufi, miracle et causalité, Abel et la clef tragiquement retournée.",
    "section-viii": "A-M-A' contre K-L-M : la loi du chiffre, la théogonie transhumaniste, Gaza, et le programme de résistance lestée.",
    "section-ix":   "Les trois usages du yaqîn (Abel, Abraham, Muhammad), la rotation K-L-M opérative, et Moïse contre Pharaon.",
    "section-xi":   "Le trésor des orphelins, la patience initiatique de Khidr, et le dernier tour de piste de l'Amour.",
}


def get_meta(html, name):
    m = re.search(rf'<meta name="{name}" content="([^"]*)"', html)
    return m.group(1) if m else ""


def clean_inline(text):
    """Minimal inline cleanup: arrows and spans only. em/strong stay as HTML."""
    text = re.sub(r'<span class="math inline">([^<]*)</span>', lambda m: m.group(1), text)
    text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)
    return text


def process_html(html_path, slug, section_number):
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    # --- Metadata ---
    c_title  = get_meta(html, "citation_title")
    c_author = get_meta(html, "citation_author")
    c_date   = get_meta(html, "citation_publication_date")
    c_journ  = get_meta(html, "citation_journal_title")
    c_url    = get_meta(html, "citation_public_url")
    c_pdf    = get_meta(html, "citation_pdf_url")
    c_lang   = get_meta(html, "citation_language")

    # --- Extract article ---
    art_m = re.search(r'<article>(.*?)</article>', html, re.DOTALL)
    if not art_m:
        print(f"  WARNING: no <article> in {html_path}")
        return
    article = art_m.group(1)

    # Remove header (contains h1 with title — handled by SectionLayout)
    article = re.sub(r'<header>.*?</header>', '', article, flags=re.DOTALL)

    # --- Extract bibliography ---
    bib_m = re.search(r'<section id="bibliographie">(.*?)</section>', article, re.DOTALL)
    bib_md = ""
    if bib_m:
        bib_html = bib_m.group(1)
        article  = article.replace(bib_m.group(0), "")
        bib_html = re.sub(r'<h2>.*?</h2>', '', bib_html, flags=re.DOTALL)
        li_items = re.findall(r'<li>(.*?)</li>', bib_html, re.DOTALL)
        bib_md = "\n## Bibliographie\n\n"
        for item in li_items:
            item = clean_inline(item.strip())
            bib_md += f"- {item}\n"

    # --- Strip section/comment wrappers ---
    article = re.sub(r'<!--.*?-->', '', article, flags=re.DOTALL)
    article = re.sub(r'<section[^>]*>', '', article)
    article = re.sub(r'</section>', '', article)

    # --- Convert intertitre paragraphs (HTML block, keep em as HTML) ---
    def cvt_intertitre(m):
        inner = clean_inline(m.group(1).strip())
        return f'\n<p class="intertitre">{inner}</p>\n'
    article = re.sub(r'<p class="intertitre">(.*?)</p>', cvt_intertitre, article, flags=re.DOTALL)

    # --- Convert h2 (markdown heading — em becomes *...*) ---
    def cvt_h2(m):
        inner = clean_inline(m.group(1).strip())
        # Convert em/strong to markdown inside headings
        inner = re.sub(r'<em>(.*?)</em>', r'*\1*', inner, flags=re.DOTALL)
        inner = re.sub(r'<strong>(.*?)</strong>', r'**\1**', inner, flags=re.DOTALL)
        return f'\n## {inner}\n'
    article = re.sub(r'<h2>(.*?)</h2>', cvt_h2, article, flags=re.DOTALL)

    # --- Convert regular paragraphs (keep em/strong as HTML inline) ---
    def cvt_p(m):
        inner = clean_inline(m.group(1).strip())
        if not inner:
            return ''
        return f'\n{inner}\n'
    article = re.sub(r'<p>(.*?)</p>', cvt_p, article, flags=re.DOTALL)

    # --- Clean whitespace ---
    article = re.sub(r'\n[ \t]+\n', '\n\n', article)  # collapse whitespace-only lines
    article = re.sub(r'\n{3,}', '\n\n', article).strip()

    # --- Frontmatter ---
    title = TITLES.get(slug, slug)
    desc  = DESCRIPTIONS.get(slug, "")

    def yq(s):
        """Escape for YAML double-quoted string."""
        return s.replace('\\', '\\\\').replace('"', '\\"')

    frontmatter = f'''---
title: "{yq(title)}"
sectionNumber: {section_number}
description: "{yq(desc)}"
slug: "{slug}"
citationTitle: "{yq(c_title)}"
citationAuthor: "{yq(c_author)}"
citationPublicationDate: "{c_date}"
citationJournalTitle: "{yq(c_journ)}"
citationPublicUrl: "{c_url}"
citationPdfUrl: "{c_pdf}"
citationLanguage: "{c_lang}"
---
'''

    full = frontmatter + '\n' + article + '\n' + bib_md

    out = os.path.join(MDX_BASE, f"{slug}.mdx")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(full)
    print(f"  ✓  {slug}.mdx")


def main():
    print("Converting HTML -> MDX...\n")
    for folder, slug, num in SECTIONS:
        folder_path = os.path.join(HTML_BASE, folder)
        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        if not html_files:
            print(f"  SKIP (no HTML): {folder}")
            continue
        process_html(os.path.join(folder_path, html_files[0]), slug, num)

    # Section X placeholder (no HTML source)
    placeholder = '''---
title: "Section X"
sectionNumber: 10
description: "Section X — contenu à paraître."
slug: "section-x"
citationTitle: "Section X"
citationAuthor: "Cédric Stéphany"
citationPublicationDate: "2026/06/20"
citationJournalTitle: "Apocalypse Circus"
citationPublicUrl: "https://apocalypsecircus.fr/section-x.html"
citationPdfUrl: "https://apocalypsecircus.fr/section-x.pdf"
citationLanguage: "fr"
---

*Section X — contenu à paraître.*
'''
    out = os.path.join(MDX_BASE, "section-x.mdx")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(placeholder)
    print("  ✓  section-x.mdx (placeholder)")

    print("\nDone.")


if __name__ == "__main__":
    main()
