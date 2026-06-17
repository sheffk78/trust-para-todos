// Trust Para Todos — Email Sequences (Spanish)
// For Brevo (Sendinblue) transactional emails

// ==========================================
// WELCOME SEQUENCE (Post-Purchase)
// ==========================================

export const welcomeSequence = [
  {
    day: 0,
    subject: "¡Felicidades! Tu paquete Trust Para Todos está en proceso",
    content: `Hola {{nombre}},

Gracias por confiar en Trust Para Todos para proteger a tu familia.

Tu pedido ha sido recibido y estamos trabajando en él. Esto es lo que sigue:

1. Generaremos tus documentos de trust (24-48 horas)
2. Te enviaremos un enlace para agendar tu cita notarial virtual
3. Tramitaremos tu EIN ante el IRS
4. Recibirás todo listo para proteger tu patrimonio

Mientras tanto, puedes ver el estado de tu pedido en tu panel:
{{panel_link}}

Si tienes alguna pregunta, responde a este correo o escríbenos por WhatsApp.

Tu tranquilidad es lo más importante. Estamos aquí para cuidarte.

— El equipo de Trust Para Todos`
  },
  {
    day: 1,
    subject: "Próximo paso: tu cita notarial",
    content: `Hola {{nombre}},

Tus documentos están casi listos. El siguiente paso es agendar tu cita notarial.

La cita es virtual (por videollamada) y dura aproximadamente 15 minutos. Necesitarás:
- Una identificación oficial (INE, pasaporte)
- Estar en un lugar tranquilo con buena conexión a internet

Agenda tu cita aquí: {{notary_link}}

El notario es bilingüe y te guiará en español.

— El equipo de Trust Para Todos`
  },
  {
    day: 2,
    subject: "Mientras esperas: aprende cómo funciona tu trust",
    content: `Hola {{nombre}},

Sabemos que esto puede ser nuevo para ti. Por eso hemos preparado un curso gratuito llamado "Trustee 101" que explica todo en español simple:

- ¿Qué es un trust y cómo funciona?
- ¿Cuáles son tus responsabilidades?
- ¿Cómo administrar los bienes del trust?
- ¿Qué hacer en caso de emergencia?

Accede al curso aquí: {{course_link}}

Son lecciones cortas, de 3-5 minutos cada una.

— El equipo de Trust Para Todos`
  },
  {
    day: 3,
    subject: "Tus documentos están listos",
    content: `Hola {{nombre}},

¡Buenas noticias! Tus documentos de trust ya están listos.

Descárgalos aquí: {{documents_link}}

Tu paquete incluye:
- Documento de trust (firmado electrónicamente)
- Guía explicativa en español
- Instrucciones para transferir tus bienes al trust

Próximo paso: agenda tu cita notarial si no lo has hecho ya.

— El equipo de Trust Para Todos`
  },
  {
    day: 5,
    subject: "¿Qué sigue? Cómo usar tu trust",
    content: `Hola {{nombre}},

¡Felicidades! Tu trust ya está activo. Aquí tienes los siguientes pasos:

1. Transfiere tu casa al trust (te enviamos las instrucciones)
2. Cambia tus cuentas bancarias e inversiones al nombre del trust
3. Actualiza tus beneficiarios en seguros de vida
4. Guarda tu documento de trust en un lugar seguro

Tu panel de TrustOffice te ayudará a mantener todo organizado:
{{trustoffice_link}}

¿Necesitas ayuda con algún paso? Escríbenos.

— El equipo de Trust Para Todos`
  },
  {
    day: 7,
    subject: "¿Quieres proteger tu patrimonio con un seguro de vida?",
    content: `Hola {{nombre}},

Ahora que tu trust está activo, queremos asegurarnos de que tengas protección completa.

Un seguro de vida puede:
- Proteger a tu familia si algo te pasa
- Pagar la hipoteca de tu casa
- Cubrir los estudios de tus hijos
- Complementar tu trust

Un agidente de seguros de confianza puede ayudarte a encontrar la mejor opción para tu familia.

¿Quieres que te contactemos? Haz clic aquí: {{insurance_link}}

Sin compromiso. Solo información.

— El equipo de Trust Para Todos`
  }
];

// ==========================================
// LEAD NURTURE SEQUENCE (Pre-Purchase)
// ==========================================

export const leadSequence = [
  {
    day: 0,
    subject: "¿Sabías que tus seres queridos podrían perder tu casa?",
    content: `Hola {{nombre}},

Gracias por visitar Trust Para Todos.

Quizás no sabías esto: cuando una persona fallece en Estados Unidos, el gobierno puede cobrar hasta el 40% de su patrimonio en impuestos de herencia.

Para personas con visa I-10, la exención es de solo $60,000. Eso significa que si tienes una casa valorada en $300,000, el IRS puede reclamar $96,000 antes de que tu familia herede.

Pero hay una solución: un trust.

En nuestro próximo correo te explicamos cómo funciona.

— El equipo de Trust Para Todos`
  },
  {
    day: 1,
    subject: "Cómo funciona un trust (explicado simple)",
    content: `Hola {{nombre}},

Un trust es un acuerdo legal que funciona como una caja fuerte para tus bienes.

 Así funciona:
1. Creas el trust (nosotros te ayudamos)
2. Pones tus bienes dentro (tu casa, tu dinero)
3. Nombres a alguien de confianza para administrarlo
4. Cuando tú no estés, tus bienes pasan a tu familia sin impuestos ni corte

Y lo mejor: tú mantienes el control total mientras vives. Puedes comprar, vender, cambiar de opinión. Es tuyo.

Haz clic aquí para ver si un trust es adecuado para ti:
{{evaluation_link}}

— El equipo de Trust Para Todos`
  },
  {
    day: 2,
    subject: "3 razones por las que tu familia necesita protección",
    content: `Hola {{nombre}},

Aquí tienes 3 razones por las que un trust es esencial para tu familia:

1. 🏠 Evitas que el gobierno se quede con tu casa
   Sin un trust, el IRS puede cobrar hasta el 40% de tu patrimonio.

2. ⏱️ Evitas meses en la corte de sucesiones
   El "probate" puede durar 6-12 meses. Un trust lo evita completamente.

3. 🙈 Privacidad para tu familia
   El probate es público. Cualquiera puede ver lo que heredaste. Un trust es privado.

Tu familia merece estar protegida. Y cuesta mucho menos de lo que imaginas.

{{evaluation_link}}

— El equipo de Trust Para Todos`
  },
  {
    day: 3,
    subject: "Lo que dicen nuestras familias",
    content: `Hola {{nombre}},

No tienes que creernos a nosotros. Esto es lo que dicen familias como la tuya:

"El proceso fue muy sencillo. Todo en español, todo en línea. En menos de una semana ya tenía mi trust listo." — Carlos R., Houston, TX

"Nunca supe que mi casa podía estar en riesgo. Gracias a Trust Para Todos, ahora sé que está protegida." — María G., Los Ángeles, CA

"Había ido con un abogado y me quería cobrar $3,500. Trust Para Todos me dio exactamente lo mismo por $997." — Ana M., Phoenix, AZ

Únete a miles de familias que ya están protegidas:
{{evaluation_link}}

— El equipo de Trust Para Todos`
  },
  {
    day: 5,
    subject: "Oferta especial: protege tu hogar hoy",
    content: `Hola {{nombre}},

Sabemos que proteger a tu familia es importante. Y queremos que sea fácil para ti.

Por tiempo limitado, menciona este código y recibe un 10% de descuento en tu paquete Trust Para Todos:

🎁 Código: FAMILIA10

 tu evaluación gratuita hoy (3 minutos) y usa el código al comprar.

{{evaluation_link}}

Tu tranquilidad no tiene precio. Pero proteger a tu familia cuesta solo $997.

— El equipo de Trust Para Todos`
  }
];