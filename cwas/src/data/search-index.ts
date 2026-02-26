import promptLibraryData from "../content/prompt-library.json";
import { toolLinks } from "./site";

export interface SearchEntry {
  id: string;
  title: string;
  href: string;
  type: "Sida" | "Sektion" | "Verktyg" | "Prompt";
  category?: string;
  tags?: string[];
  excerpt: string;
}

const promptEntries: SearchEntry[] = (promptLibraryData as any[]).map((prompt) => ({
  id: `prompt-${prompt.id}`,
  title: prompt.title,
  href: `/promptbibliotek#${prompt.category === "Skolbibliotek/MIK" ? "skolbibliotek-mik" : prompt.category.toLowerCase().replaceAll(" ", "-")}`,
  type: "Prompt",
  category: prompt.category,
  tags: prompt.tags,
  excerpt: prompt.summary
}));

const toolEntries: SearchEntry[] = toolLinks.map((tool) => ({
  id: `tool-${tool.href}`,
  title: tool.label,
  href: tool.href,
  type: "Verktyg",
  category: tool.categories.join(", "),
  tags: tool.categories,
  excerpt: tool.description || "Verktygssida for CWas"
}));

const staticEntries: SearchEntry[] = [
  {
    id: "page-start",
    title: "Start",
    href: "/",
    type: "Sida",
    category: "Översikt",
    excerpt: "Startpunkt för CWas AI-handbok med snabba startspår, trygg start och navigering."
  },
  {
    id: "page-profil",
    title: "Profil och behov",
    href: "/profil-behov",
    type: "Sida",
    category: "Profil",
    excerpt: "Behovsbild för CWas: styrkor, friktion, integritet och vad handboken ska stötta."
  },
  {
    id: "page-verktyg",
    title: "Verktyg",
    href: "/verktyg",
    type: "Sida",
    category: "Verktyg",
    excerpt: "Filtrera verktyg och jämför vilket som passar för skrivande, debatt, akademiskt och integritet."
  },
  {
    id: "page-betalval",
    title: "Vilket ska jag betala for?",
    href: "/verktyg/vilket-ska-jag-betala-for",
    type: "Sida",
    category: "Verktyg",
    excerpt: "Källbaserad jämförelse av ChatGPT, Claude, Perplexity och Gemini utan nya fakta."
  },
  {
    id: "page-arbetsfloden",
    title: "Arbetsfloden",
    href: "/arbetsfloden",
    type: "Sida",
    category: "Workflow",
    excerpt: "Tidssatta arbetsflöden med steg, checklistor och copybara prompts."
  },
  {
    id: "wf-politisk-text",
    title: "Politisk text 30 min",
    href: "/arbetsfloden#politisk-text-30-min",
    type: "Sektion",
    category: "Workflow",
    tags: ["skrivande", "politik", "faktakoll"],
    excerpt: "Workflow för utkast, tonrunda, faktakollista och slutgranskning."
  },
  {
    id: "wf-debatt",
    title: "Debatt 10 min",
    href: "/arbetsfloden#debatt-10-min",
    type: "Sektion",
    category: "Workflow",
    tags: ["debatt", "muntligt", "strategi"],
    excerpt: "Kort drill för tes, invändningar, friktion och nödmeningar."
  },
  {
    id: "wf-akademiskt",
    title: "Akademisk artikel 20 min",
    href: "/arbetsfloden#akademisk-artikel-20-min",
    type: "Sektion",
    category: "Workflow",
    tags: ["akademiskt", "ordlista", "seminarium"],
    excerpt: "Snabb översikt, ordlista, kritiska frågor och citeringsspår."
  },
  {
    id: "wf-arshjul",
    title: "Skolbiblioteksplan / arshjul",
    href: "/arbetsfloden#skolbiblioteksplan-arshjul",
    type: "Sektion",
    category: "Workflow",
    tags: ["skolbibliotek", "MIK", "planering"],
    excerpt: "Planeringsworkflow för skolbiblioteksplan, årshjul och uppföljning."
  },
  {
    id: "page-promptbibliotek",
    title: "Promptbibliotek",
    href: "/promptbibliotek",
    type: "Sida",
    category: "Prompts",
    excerpt: "Datadrivet promptbibliotek med filter och kopiera-knapp."
  },
  {
    id: "page-integritet",
    title: "Integritet och trygg användning",
    href: "/integritet-gdpr",
    type: "Sida",
    category: "Integritet",
    excerpt: "Praktiska regler för anonymisering, mikrofonbehörigheter och data controls."
  },
  {
    id: "int-anonymisering",
    title: "Anonymisering och minimering",
    href: "/integritet-gdpr#anonymisering",
    type: "Sektion",
    category: "Integritet",
    tags: ["anonymisering", "dataminimering"],
    excerpt: "Steg för steg-rutin för att ta bort identifierare och minska risk."
  },
  {
    id: "int-mikrofon",
    title: "Mikrofonbehörigheter och röstläge",
    href: "/integritet-gdpr#mikrofon-behorigheter",
    type: "Sektion",
    category: "Integritet",
    tags: ["mikrofon", "behorigheter", "rostlage"],
    excerpt: "Neutral och praktisk vägledning för mikrofonbehörighet och textläge som alternativ."
  },
  {
    id: "int-data-controls",
    title: "Data controls",
    href: "/integritet-gdpr#data-controls",
    type: "Sektion",
    category: "Integritet",
    tags: ["data controls", "inställningar", "integritet"],
    excerpt: "Neutral förklaring av datadelning, historik och tillfälliga chattar som extra kontroll."
  },
  {
    id: "page-tips",
    title: "Tips och trix",
    href: "/tips-trix",
    type: "Sida",
    category: "Tips",
    excerpt: "Allmän AI-kunskap, kvalitetstänk och effektivare arbetssätt."
  },
  {
    id: "tips-prompting",
    title: "Prompting som ger bättre svar",
    href: "/tips-trix#prompting",
    type: "Sektion",
    category: "Tips",
    tags: ["prompting", "gratislage", "struktur"],
    excerpt: "Korta promptvanor som ger bättre svar utan onödigt långa instruktioner."
  },
  {
    id: "tips-kvalitet",
    title: "Kvalitetskontroll och faktagranskning",
    href: "/tips-trix#kvalitetskontroll",
    type: "Sektion",
    category: "Tips",
    tags: ["faktakoll", "kritik", "[KOLLA]"],
    excerpt: "Snabb rutin för att skilja språkstöd från sakstöd och kontrollera riskpunkter."
  },
  {
    id: "tips-fallgropar",
    title: "Vanliga fallgropar",
    href: "/tips-trix#vanliga-fallgropar",
    type: "Sektion",
    category: "Tips",
    tags: ["fallgropar", "tempo", "granskning"],
    excerpt: "Vanliga misstag och tecken på att stanna upp och starta om smartare."
  },
  {
    id: "page-om-guiden",
    title: "Om handboken",
    href: "/om-guiden",
    type: "Sida",
    category: "Om guiden",
    excerpt: "Kort sida om underlag, arbetssätt och hur guiden hålls aktuell."
  },
  {
    id: "page-qa",
    title: "QA-checklista",
    href: "/qa-checklista",
    type: "Sida",
    category: "QA",
    tags: ["qa", "checklista", "publicering", "sök", "filter"],
    excerpt: "Manuell QA-checklista för innehåll, sök, filter, navigation och publicering."
  }
];

export const searchIndex: SearchEntry[] = [...staticEntries, ...toolEntries, ...promptEntries];
