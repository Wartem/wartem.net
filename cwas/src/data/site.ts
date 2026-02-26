export interface LinkItem {
  label: string;
  href: string;
  description?: string;
}

export type ToolFilterCategory = "Skriv" | "Debatt" | "Akademiskt" | "Integritet";

export interface ToolLinkItem extends LinkItem {
  categories: ToolFilterCategory[];
  priorityNote?: string;
}

export const siteNav: LinkItem[] = [
  { label: "Start", href: "/" },
  { label: "Sök", href: "/sok" },
  { label: "Profil och behov", href: "/profil-behov" },
  { label: "Verktyg", href: "/verktyg" },
  { label: "Arbetsflöden", href: "/arbetsfloden" },
  { label: "Promptbibliotek", href: "/promptbibliotek" },
  { label: "Integritet och GDPR", href: "/integritet-gdpr" },
  { label: "Tips och trix", href: "/tips-trix" }
];

export const toolFilterCategories: ToolFilterCategory[] = ["Skriv", "Debatt", "Akademiskt", "Integritet"];

export const toolLinks: ToolLinkItem[] = [
  {
    label: "ChatGPT",
    href: "/verktyg/chatgpt",
    description: "Bred skrivhjälp, debattträning (text/röst), struktur och planering.",
    categories: ["Skriv", "Debatt", "Akademiskt"]
  },
  {
    label: "Claude",
    href: "/verktyg/claude",
    description: "Nyanserad textbearbetning, längre resonemang, dokument och debattträning i text.",
    categories: ["Skriv", "Debatt", "Akademiskt"]
  },
  {
    label: "Perplexity",
    href: "/verktyg/perplexity",
    description: "Research med källspår, snabb faktakontroll och citeringsorientering.",
    categories: ["Akademiskt", "Integritet"]
  },
  {
    label: "Gemini",
    href: "/verktyg/gemini",
    description: "Google-nära arbetsflöden, brainstorming och dokumentstöd.",
    categories: ["Skriv", "Debatt", "Akademiskt", "Integritet"]
  },
  {
    label: "NotebookLM",
    href: "/verktyg/notebooklm",
    description: "Arbete på egna dokument, källbaserad översikt och ljudöversikter.",
    categories: ["Akademiskt", "Integritet"]
  },
  {
    label: "LanguageTool / Microsoft Editor",
    href: "/verktyg/sprakstod",
    description: "Språkgranskning, stil, tydlighet och korrektur på svenska texter.",
    categories: ["Skriv", "Integritet"]
  },
  {
    label: "Lokala alternativ",
    href: "/verktyg/lokala-alternativ",
    description: "Lokala/offline alternativ för högre integritet och dokumentarbete.",
    categories: ["Skriv", "Akademiskt", "Integritet"]
  }
];

export const startQuickLinks: LinkItem[] = [
  {
    label: "Hur sajten används",
    href: "#hur-sajten-anvands",
    description: "Kort guide till hur CWas kan jobba med sidan i vardagen."
  },
  {
    label: "Verktygsöversikt",
    href: "/verktyg",
    description: "Indexsida för verktyg och vidare undersidor."
  },
  {
    label: "Arbetsflöden",
    href: "/arbetsfloden",
    description: "Praktiska tidssatta flöden för olika uppgifter."
  },
  {
    label: "Promptbibliotek",
    href: "/promptbibliotek",
    description: "Mallar efter skrivsituation och arbetskontext."
  },
  {
    label: "Integritet och GDPR",
    href: "/integritet-gdpr",
    description: "Praktiska regler och bedömningar för vardagsanvändning."
  },
  {
    label: "Tips och trix",
    href: "/tips-trix",
    description: "Allmän AI-kunskap, kvalitetstänk och effektivisering."
  }
];
