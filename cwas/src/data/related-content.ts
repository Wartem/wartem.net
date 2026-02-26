import type { LinkItem } from "./site";

export const relatedContentByPath: Record<string, LinkItem[]> = {
  "/profil-behov": [
    { label: "Arbetsflöden", href: "/arbetsfloden", description: "Tidsatta arbetssätt som matchar behoven." },
    { label: "Promptbibliotek", href: "/promptbibliotek", description: "Korta promptmallar för CWas vardag." },
    { label: "Integritet och trygg användning", href: "/integritet-gdpr", description: "Praktiska regler och checklistor." }
  ],
  "/arbetsfloden": [
    { label: "Promptbibliotek", href: "/promptbibliotek", description: "Filtrera och kopiera korta prompts per kategori." },
    { label: "Verktyg", href: "/verktyg", description: "Välj verktyg efter skriv/debatt/akademiskt/integritet." },
    { label: "Integritet och trygg användning", href: "/integritet-gdpr", description: "Viktigt innan du klistrar in underlag." }
  ],
  "/promptbibliotek": [
    { label: "Arbetsflöden", href: "/arbetsfloden", description: "Använd prompts tillsammans med steg-för-steg-flöden." },
    { label: "Verktyg", href: "/verktyg", description: "Se vilket verktyg som passar för varje prompttyp." },
    { label: "Sök", href: "/sok", description: "Sök i prompts, verktyg, workflows och sektioner." }
  ],
  "/integritet-gdpr": [
    { label: "Lokala alternativ", href: "/verktyg/lokala-alternativ", description: "När extern AI inte passar för uppgiften." },
    { label: "Arbetsflöden", href: "/arbetsfloden", description: "Workflows med [KOLLA]/[OSÄKERT]-rutiner." },
    { label: "Sök", href: "/sok", description: "Hitta relevanta prompts och sektioner snabbt." }
  ],
  "/verktyg": [
    { label: "Vilket ska jag betala för?", href: "/verktyg/vilket-ska-jag-betala-for", description: "Källbaserad jämförelse utan nya fakta." },
    { label: "Promptbibliotek", href: "/promptbibliotek", description: "Korta prompts som fungerar i gratisläge." },
    { label: "Sök", href: "/sok", description: "Sök i verktyg, prompts och workflows." }
  ],
  "/verktyg/vilket-ska-jag-betala-for": [
    { label: "Verktygsindex", href: "/verktyg", description: "Filtrera verktyg efter behov." },
    { label: "ChatGPT", href: "/verktyg/chatgpt", description: "Bred vardagsnytta och debattträning." },
    { label: "Claude", href: "/verktyg/claude", description: "Nyanserad text och akademisk översikt." }
  ],
  "/sok": [
    { label: "Promptbibliotek", href: "/promptbibliotek", description: "Filtrera prompts per kategori och tagg." },
    { label: "Verktyg", href: "/verktyg", description: "Filtrera verktyg och jämför alternativ." },
    { label: "Arbetsflöden", href: "/arbetsfloden", description: "Gå direkt till workflows efter sökning." }
  ],
  "/tips-trix": [
    { label: "Promptbibliotek", href: "/promptbibliotek", description: "Korta prompts att kombinera med tipsen." },
    { label: "Arbetsflöden", href: "/arbetsfloden", description: "Använd tipsen i faktiska steg-för-steg-flöden." },
    { label: "Verktyg", href: "/verktyg", description: "Jämför verktyg när det faktiskt lönar sig." }
  ],
  "/om-guiden": [
    { label: "Start", href: "/", description: "Tillbaka till introduktion och startspår." },
    { label: "Sök", href: "/sok", description: "Sök i hela handboken." },
    { label: "Promptbibliotek", href: "/promptbibliotek", description: "Se datadrivna prompts med filter och kopiera." },
    { label: "QA-checklista", href: "/qa-checklista", description: "Manuell genomgång före publicering och större ändringar." }
  ],
  "/qa-checklista": [
    { label: "Sök", href: "/sok", description: "Testa sökresultat som del av QA-rundan." },
    { label: "Verktyg", href: "/verktyg", description: "Kontrollera filter och verktygssidor." },
    { label: "Promptbibliotek", href: "/promptbibliotek", description: "Kontrollera filter + kopiera-knappar." }
  ]
};
