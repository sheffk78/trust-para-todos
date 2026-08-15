export interface BlogArticle {
  slug: string;
  title: string;
  tag: string;
  image: string;
  related: { slug: string; title: string; tag: string; image: string }[];
}

export const articles: BlogArticle[] = [
  {
    slug: 'que-es-trust-revocable',
    title: '¿Qué es un trust revocable? Explicación completa en español',
    tag: 'Educacional',
    image: '/images/blog/01-hero-family-home.jpg',
    related: [
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento: ¿Cuál es Mejor?', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.jpg' },
      { slug: 'cuanto-cuesta-fideicomiso', title: '¿Cuánto Cuesta un Fideicomiso?', tag: 'Precios', image: '/images/blog/05-hero-financial-planning.jpg' },
      { slug: 'fideicomiso-revocable-vs-irrevocable', title: 'Revocable vs Irrevocable', tag: 'Comparativa', image: '/images/blog/08-hero-family-property.jpg' }
    ]
  },
  {
    slug: 'como-crear-trust-online',
    title: 'Cómo crear un trust online en español: paso a paso',
    tag: 'Guía',
    image: '/images/blog/02-hero-documents.jpg',
    related: [
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado para un Trust?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.jpg' },
      { slug: 'cuanto-cuesta-fideicomiso', title: '¿Cuánto Cuesta un Fideicomiso?', tag: 'Precios', image: '/images/blog/05-hero-financial-planning.jpg' },
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.jpg' }
    ]
  },
  {
    slug: 'seguro-vida-trust',
    title: 'Seguro de vida + trust: por qué necesitas ambos',
    tag: 'Protección',
    image: '/images/blog/03-hero-family-protection.jpg',
    related: [
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.jpg' },
      { slug: 'que-es-probate-como-evitarlo', title: '¿Qué es el Probate?', tag: 'Educacional', image: '/images/blog/07-hero-courtroom.jpg' },
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.jpg' }
    ]
  },
  {
    slug: 'trust-vs-testamento',
    title: 'Trust vs Testamento: ¿Cuál es Mejor para Proteger a Tu Familia?',
    tag: 'Comparativa',
    image: '/images/blog/04-hero-senior-couple.jpg',
    related: [
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.jpg' },
      { slug: 'que-es-probate-como-evitarlo', title: '¿Qué es el Probate?', tag: 'Educacional', image: '/images/blog/07-hero-courtroom.jpg' },
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.jpg' }
    ]
  },
  {
    slug: 'cuanto-cuesta-fideicomiso',
    title: '¿Cuánto Cuesta un Fideicomiso en Estados Unidos? (Comparativa 2026)',
    tag: 'Precios',
    image: '/images/blog/05-hero-financial-planning.jpg',
    related: [
      { slug: 'como-crear-trust-online', title: 'Cómo Crear un Trust Online', tag: 'Guía', image: '/images/blog/02-hero-documents.jpg' },
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.jpg' },
      { slug: 'seguro-vida-trust', title: 'Seguro de Vida + Trust', tag: 'Protección', image: '/images/blog/03-hero-family-protection.jpg' }
    ]
  },
  {
    slug: 'necesito-abogado-trust',
    title: '¿Necesito un Abogado para Hacer un Trust? La Verdad',
    tag: 'Decisiones',
    image: '/images/blog/06-hero-consultation.jpg',
    related: [
      { slug: 'como-crear-trust-online', title: 'Cómo Crear un Trust Online', tag: 'Guía', image: '/images/blog/02-hero-documents.jpg' },
      { slug: 'cuanto-cuesta-fideicomiso', title: '¿Cuánto Cuesta un Fideicomiso?', tag: 'Precios', image: '/images/blog/05-hero-financial-planning.jpg' },
      { slug: 'fideicomiso-revocable-vs-irrevocable', title: 'Revocable vs Irrevocable', tag: 'Comparativa', image: '/images/blog/08-hero-family-property.jpg' }
    ]
  },
  {
    slug: 'que-es-probate-como-evitarlo',
    title: '¿Qué es el Probate y Cómo Evitarlo en Estados Unidos?',
    tag: 'Educacional',
    image: '/images/blog/07-hero-courtroom.jpg',
    related: [
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.jpg' },
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.jpg' },
      { slug: 'seguro-vida-trust', title: 'Seguro de Vida + Trust', tag: 'Protección', image: '/images/blog/03-hero-family-protection.jpg' }
    ]
  },
  {
    slug: 'fideicomiso-revocable-vs-irrevocable',
    title: 'Fideicomiso Revocable vs Irrevocable: Diferencias Explicadas',
    tag: 'Comparativa',
    image: '/images/blog/08-hero-family-property.jpg',
    related: [
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.jpg' },
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.jpg' },
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.jpg' }
    ]
  }
];

export function getRelated(slug: string) {
  const article = articles.find(a => a.slug === slug);
  return article?.related ?? [];
}