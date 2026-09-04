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
    image: '/images/blog/01-hero-family-home.webp',
    related: [
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento: ¿Cuál es Mejor?', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.webp' },
      { slug: 'cuanto-cuesta-fideicomiso', title: '¿Cuánto Cuesta un Fideicomiso?', tag: 'Precios', image: '/images/blog/05-hero-financial-planning.webp' },
      { slug: 'fideicomiso-revocable-vs-irrevocable', title: 'Revocable vs Irrevocable', tag: 'Comparativa', image: '/images/blog/08-hero-family-property.webp' }
    ]
  },
  {
    slug: 'como-crear-trust-online',
    title: 'Cómo crear un trust online en español: paso a paso',
    tag: 'Guía',
    image: '/images/blog/02-hero-documents.webp',
    related: [
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado para un Trust?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.webp' },
      { slug: 'cuanto-cuesta-fideicomiso', title: '¿Cuánto Cuesta un Fideicomiso?', tag: 'Precios', image: '/images/blog/05-hero-financial-planning.webp' },
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.webp' }
    ]
  },
  {
    slug: 'seguro-vida-trust',
    title: 'Seguro de vida + trust: por qué necesitas ambos',
    tag: 'Protección',
    image: '/images/blog/03-hero-family-protection.webp',
    related: [
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.webp' },
      { slug: 'que-es-probate-como-evitarlo', title: '¿Qué es el Probate?', tag: 'Educacional', image: '/images/blog/07-hero-courtroom.webp' },
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.webp' }
    ]
  },
  {
    slug: 'trust-vs-testamento',
    title: 'Trust vs Testamento: ¿Cuál es Mejor para Proteger a Tu Familia?',
    tag: 'Comparativa',
    image: '/images/blog/04-hero-senior-couple.webp',
    related: [
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.webp' },
      { slug: 'que-es-probate-como-evitarlo', title: '¿Qué es el Probate?', tag: 'Educacional', image: '/images/blog/07-hero-courtroom.webp' },
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.webp' }
    ]
  },
  {
    slug: 'cuanto-cuesta-fideicomiso',
    title: '¿Cuánto Cuesta un Fideicomiso en Estados Unidos? (Comparativa 2026)',
    tag: 'Precios',
    image: '/images/blog/05-hero-financial-planning.webp',
    related: [
      { slug: 'como-crear-trust-online', title: 'Cómo Crear un Trust Online', tag: 'Guía', image: '/images/blog/02-hero-documents.webp' },
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.webp' },
      { slug: 'seguro-vida-trust', title: 'Seguro de Vida + Trust', tag: 'Protección', image: '/images/blog/03-hero-family-protection.webp' }
    ]
  },
  {
    slug: 'necesito-abogado-trust',
    title: '¿Necesito un Abogado para Hacer un Trust? La Verdad',
    tag: 'Decisiones',
    image: '/images/blog/06-hero-consultation.webp',
    related: [
      { slug: 'como-crear-trust-online', title: 'Cómo Crear un Trust Online', tag: 'Guía', image: '/images/blog/02-hero-documents.webp' },
      { slug: 'cuanto-cuesta-fideicomiso', title: '¿Cuánto Cuesta un Fideicomiso?', tag: 'Precios', image: '/images/blog/05-hero-financial-planning.webp' },
      { slug: 'fideicomiso-revocable-vs-irrevocable', title: 'Revocable vs Irrevocable', tag: 'Comparativa', image: '/images/blog/08-hero-family-property.webp' }
    ]
  },
  {
    slug: 'que-es-probate-como-evitarlo',
    title: '¿Qué es el Probate y Cómo Evitarlo en Estados Unidos?',
    tag: 'Educacional',
    image: '/images/blog/07-hero-courtroom.webp',
    related: [
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.webp' },
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.webp' },
      { slug: 'seguro-vida-trust', title: 'Seguro de Vida + Trust', tag: 'Protección', image: '/images/blog/03-hero-family-protection.webp' }
    ]
  },
  {
    slug: 'fideicomiso-revocable-vs-irrevocable',
    title: 'Fideicomiso Revocable vs Irrevocable: Diferencias Explicadas',
    tag: 'Comparativa',
    image: '/images/blog/08-hero-family-property.webp',
    related: [
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.webp' },
      { slug: 'necesito-abogado-trust', title: '¿Necesito un Abogado?', tag: 'Decisiones', image: '/images/blog/06-hero-consultation.webp' },
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.webp' }
    ]
  },
  {
    slug: 'trust-en-espanol',
    title: 'Trust en español: guía completa para familias mexicanas',
    tag: 'Educacional',
    image: '/images/blog/01-hero-family-home.webp',
    related: [
      { slug: 'que-es-trust-revocable', title: '¿Qué es un Trust Revocable?', tag: 'Educacional', image: '/images/blog/01-hero-family-home.webp' },
      { slug: 'trust-vs-testamento', title: 'Trust vs Testamento', tag: 'Comparativa', image: '/images/blog/04-hero-senior-couple.webp' },
      { slug: 'cuanto-cuesta-fideicomiso', title: '¿Cuánto Cuesta un Fideicomiso?', tag: 'Precios', image: '/images/blog/05-hero-financial-planning.webp' }
    ]
  }
];

export function getRelated(slug: string) {
  const article = articles.find(a => a.slug === slug);
  return article?.related ?? [];
}