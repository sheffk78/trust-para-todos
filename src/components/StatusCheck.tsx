import { useState } from 'react';

const STEPS = [
  {
    title: 'Tu Información',
    fields: [
      { id: 'nombre', label: 'Nombre completo', type: 'text', required: true },
      { id: 'email', label: 'Correo electrónico', type: 'email', required: true },
      { id: 'telefono', label: 'Teléfono (WhatsApp)', type: 'tel', required: true },
      { id: 'visa', label: 'Tipo de visa', type: 'select', required: true, options: ['I-10', 'Green Card', 'Otra'] }
    ]
  },
  {
    title: 'Tu Residencia',
    fields: [
      { id: 'residencia', label: '¿Eres residente permanente de EE.UU.?', type: 'select', required: true, options: ['Sí', 'No'] },
      { id: 'domicilio', label: '¿Dónde pasas la mayor parte del año?', type: 'select', required: true, options: ['Estados Unidos', 'México', 'Otro'] }
    ]
  },
  {
    title: 'Tu Familia',
    fields: [
      { id: 'estado_civil', label: 'Estado civil', type: 'select', required: true, options: ['Soltero/a', 'Casado/a', 'Divorciado/a', 'Viudo/a'] },
      { id: 'conyuge_ciudadano', label: '¿Tu cónyuge es ciudadano estadounidense?', type: 'select', required: true, options: ['Sí', 'No', 'No aplica'] },
      { id: 'hijos', label: '¿Tienes hijos?', type: 'select', required: true, options: ['Sí', 'No'] }
    ]
  },
  {
    title: 'Tus Bienes',
    fields: [
      { id: 'casa', label: '¿Tienes una casa en Estados Unidos?', type: 'select', required: true, options: ['Sí', 'No'] },
      { id: 'estado_propiedad', label: '¿En qué estado está tu propiedad?', type: 'select', required: true, options: ['California', 'Texas', 'Arizona', 'Nevada', 'Illinois', 'Otro'] },
      { id: 'valor', label: 'Valor aproximado de tu propiedad', type: 'select', required: true, options: ['$50K - $100K', '$100K - $250K', '$250K - $500K', '$500K+'] }
    ]
  },
  {
    title: 'Referido',
    fields: [
      { id: 'codigo_afiliado', label: '¿Quién te recomendó? (Código de referido)', type: 'text', required: false }
    ]
  }
];

export default function StatusCheck() {
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, string>>({});

  const updateField = (id: string, value: string) => {
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const currentStep = STEPS[step];
  const progress = ((step + 1) / STEPS.length) * 100;
  const isLastStep = step === STEPS.length - 1;

  const canProceed = currentStep.fields
    .filter(f => f.required)
    .every(f => formData[f.id]?.trim());

  const handleNext = () => {
    if (isLastStep) {
      // Submit questionnaire to backend API
      submitQuestionnaire();
    } else {
      setStep(s => Math.min(s + 1, STEPS.length - 1));
    }
  };

  const submitQuestionnaire = async () => {
    try {
      const res = await fetch('/api/questionnaire', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        window.location.href = '/recomendacion?' + new URLSearchParams(formData).toString();
      } else {
        // Fallback: submit via URL params even if API fails
        window.location.href = '/recomendacion?' + new URLSearchParams(formData).toString();
      }
    } catch {
      window.location.href = '/recomendacion?' + new URLSearchParams(formData).toString();
    }
  };

  return (
    <div className="page-content" style={{ maxWidth: 600 }}>
      <h1 style={{ textAlign: 'center', marginBottom: 8 }}>Evaluación de Situación</h1>
      <p style={{ textAlign: 'center', color: 'var(--gray)', marginBottom: 32 }}>
        Para asegurar la máxima protección de tu familia, necesitamos saber...
      </p>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <p style={{ textAlign: 'center', color: 'var(--gray)', marginBottom: 24, fontSize: '0.9rem' }}>
        Paso {step + 1} de {STEPS.length}: <strong>{currentStep.title}</strong>
      </p>

      {currentStep.fields.map(field => (
        <div className="form-group" key={field.id}>
          <label htmlFor={field.id}>{field.label}{field.required ? ' *' : ''}</label>
          {field.type === 'select' ? (
            <select
              id={field.id}
              value={formData[field.id] || ''}
              onChange={e => updateField(field.id, e.target.value)}
              required={field.required}
            >
              <option value="">Selecciona...</option>
              {field.options.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          ) : (
            <input
              type={field.type}
              id={field.id}
              value={formData[field.id] || ''}
              onChange={e => updateField(field.id, e.target.value)}
              required={field.required}
            />
          )}
        </div>
      ))}

      <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
        {step > 0 && (
          <button
            className="btn btn-outline"
            onClick={() => setStep(s => Math.max(s - 1, 0))}
            style={{ flex: 1 }}
          >
            Atrás
          </button>
        )}
        <button
          className={`btn ${step > 0 ? 'btn-primary' : 'btn-primary'} btn-lg`}
          onClick={handleNext}
          disabled={!canProceed}
          style={{ flex: 1, opacity: canProceed ? 1 : 0.5 }}
        >
          {isLastStep ? 'Ver mi recomendación' : 'Siguiente'}
        </button>
      </div>

      <div style={{ textAlign: 'center', marginTop: 24 }}>
        {/* TODO: Replace with real WhatsApp number */}
        <a href="https://wa.me/18001234567" style={{ color: '#25D366', fontWeight: 600, textDecoration: 'none' }}>
          💬 ¿Necesitas ayuda? Escríbenos por WhatsApp
        </a>
      </div>
    </div>
  );
}