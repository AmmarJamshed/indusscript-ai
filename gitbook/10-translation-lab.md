# Speculative Translation Lab

## Purpose

Give students and the public a **readable** English → assumed Indus symbol experience without pretending the script is cracked.

## Behaviour

1. Tokenise English
2. Skip English-only determiners
3. Map content words to transparent concept frames (trade, authority, commodity, place, …)
4. Assign unused high-frequency Indus signs weighted by positional preferences from the corpus
5. Show motif glyphs (visual proxies), proof tables, JS comparisons, assumptions, limitations
6. Hide catalogue IDs under “researchers only”

## Interfaces

| Interface | URL / command |
| --- | --- |
| GitHub Pages public demo | [https://ammarjamshed.github.io/indusscript-ai/](https://ammarjamshed.github.io/indusscript-ai/) |
| Streamlit research UI (tab 16) | `streamlit run dashboard/app.py` |

{% hint style="warning" %}
Glyphs are **readability proxies**, not curated palaeographic drawings from a sealed museum catalogue.
{% endhint %}
