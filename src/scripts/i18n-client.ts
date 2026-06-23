/**
 * Trust Para Todos — Client-side i18n
 *
 * Reads the tpt_lang cookie and translates all elements with data-i18n attributes.
 * Also provides helper functions for dynamic content (status badges, etc.).
 * Runs on DOMContentLoaded.
 */

const DICT: Record<string, { es: string; en: string }> = {
  // Admin nav
  'nav.dashboard': { es: 'Dashboard', en: 'Dashboard' },
  'nav.orders': { es: 'Órdenes', en: 'Orders' },
  'nav.customers': { es: 'Clientes', en: 'Customers' },
  'nav.back_to_site': { es: '← Volver al sitio', en: '← Back to site' },
  'nav.logout': { es: '🚪 Cerrar Sesión', en: '🚪 Logout' },
  'nav.admin_panel': { es: 'Panel de Administración', en: 'Admin Panel' },

  // Dashboard
  'dashboard.title': { es: 'Dashboard', en: 'Dashboard' },
  'dashboard.loading': { es: 'Cargando dashboard...', en: 'Loading dashboard...' },
  'dashboard.total_orders': { es: 'Total Órdenes', en: 'Total Orders' },
  'dashboard.orders_today': { es: 'Órdenes Hoy', en: 'Orders Today' },
  'dashboard.pending': { es: 'Pendientes', en: 'Pending' },
  'dashboard.revenue': { es: 'Ingresos', en: 'Revenue' },
  'dashboard.recent_orders': { es: 'Órdenes Recientes', en: 'Recent Orders' },
  'dashboard.error': { es: 'Error al cargar', en: 'Failed to load' },

  // Orders table
  'orders.title': { es: 'Órdenes', en: 'Orders' },
  'orders.customer': { es: 'Cliente', en: 'Customer' },
  'orders.email': { es: 'Email', en: 'Email' },
  'orders.plan': { es: 'Plan', en: 'Plan' },
  'orders.amount': { es: 'Monto', en: 'Amount' },
  'orders.status': { es: 'Estado', en: 'Status' },
  'orders.date': { es: 'Fecha', en: 'Date' },
  'orders.search': { es: 'Buscar órdenes...', en: 'Search orders...' },
  'orders.filter_status': { es: 'Filtrar por estado', en: 'Filter by status' },
  'orders.filter_plan': { es: 'Filtrar por plan', en: 'Filter by plan' },
  'orders.all': { es: 'Todas', en: 'All' },
  'orders.no_results': { es: 'No se encontraron órdenes', en: 'No orders found' },
  'orders.loading': { es: 'Cargando órdenes...', en: 'Loading orders...' },
  'orders.error': { es: 'Error al cargar órdenes', en: 'Error loading orders' },

  // Order detail
  'order.title': { es: 'Detalle de Orden', en: 'Order Detail' },
  'order.customer_info': { es: 'Información del Cliente', en: 'Customer Information' },
  'order.fulfillment': { es: 'Progreso de Fulfillment', en: 'Fulfillment Progress' },
  'order.documents': { es: 'Documentos', en: 'Documents' },
  'order.created': { es: 'Creada', en: 'Created' },
  'order.updated': { es: 'Actualizada', en: 'Updated' },
  'order.plan_base': { es: 'Trust Para Todos', en: 'Trust Para Todos' },
  'order.plan_completo': { es: 'Paquete Completo', en: 'Complete Package' },
  'order.generate_docs': { es: 'Regenerar Documentos', en: 'Regenerate Documents' },
  'order.download': { es: '⬇ Descargar', en: '⬇ Download' },
  'order.back': { es: '← Volver a órdenes', en: '← Back to orders' },

  // Customers
  'customers.title': { es: 'Clientes', en: 'Customers' },
  'customers.search': { es: 'Buscar clientes...', en: 'Search customers...' },
  'customers.name': { es: 'Nombre', en: 'Name' },
  'customers.email': { es: 'Email', en: 'Email' },
  'customers.phone': { es: 'Teléfono', en: 'Phone' },
  'customers.orders': { es: 'Órdenes', en: 'Orders' },
  'customers.registered': { es: 'Registrado', en: 'Registered' },
  'customers.no_results': { es: 'No se encontraron clientes', en: 'No customers found' },
  'customers.loading': { es: 'Cargando clientes...', en: 'Loading customers...' },
  'customers.error': { es: 'Error al cargar clientes', en: 'Error loading customers' },

  // Customer detail
  'customer.title': { es: 'Detalle del Cliente', en: 'Customer Detail' },
  'customer.info': { es: 'Información del Cliente', en: 'Customer Information' },
  'customer.order_history': { es: 'Historial de Órdenes', en: 'Order History' },
  'customer.back': { es: '← Volver a clientes', en: '← Back to customers' },

  // Status labels
  'status.pending': { es: 'Pendiente', en: 'Pending' },
  'status.paid': { es: 'Pagado', en: 'Paid' },
  'status.fulfilling': { es: 'En proceso', en: 'In Progress' },
  'status.complete': { es: 'Completado', en: 'Completed' },

  // Plan labels
  'plan.base': { es: 'Base', en: 'Base' },
  'plan.completo': { es: 'Completo', en: 'Complete' },

  // Fulfillment step labels
  'step.payment_confirmed': { es: 'Pago confirmado', en: 'Payment Confirmed' },
  'step.document_generation': { es: 'Generación de documentos', en: 'Document Generation' },
  'step.ein_filing': { es: 'Trámite de EIN', en: 'EIN Filing' },
  'step.notary_scheduling': { es: 'Cita notarial', en: 'Notary Scheduling' },
  'step.welcome_email': { es: 'Correo de bienvenida', en: 'Welcome Email' },
  'step.final_delivery': { es: 'Entrega final', en: 'Final Delivery' },

  // Step descriptions
  'step.desc.payment_confirmed': { es: 'Tu pago ha sido procesado exitosamente.', en: 'Your payment has been processed successfully.' },
  'step.desc.document_generation': { es: 'Tus documentos de trust están siendo preparados.', en: 'Your trust documents are being prepared.' },
  'step.desc.ein_filing': { es: 'Estamos tramitando tu EIN ante el IRS.', en: 'We are processing your EIN with the IRS.' },
  'step.desc.notary_scheduling': { es: 'Agenda tu cita notarial virtual.', en: 'Schedule your virtual notary appointment.' },
  'step.desc.welcome_email': { es: 'Recibirás instrucciones detalladas por correo.', en: 'You will receive detailed instructions by email.' },
  'step.desc.final_delivery': { es: 'Todo está listo. Tu trust está activo.', en: 'Everything is ready. Your trust is active.' },
  'step.completed': { es: 'Completado', en: 'Completed' },

  // Document labels
  'doc.trust': { es: 'Trust Revocable', en: 'Revocable Living Trust' },
  'doc.ilit': { es: 'ILIT (Seguro de Vida)', en: 'ILIT (Life Insurance)' },
  'doc.ein': { es: 'EIN (Identificación Fiscal)', en: 'EIN (Tax ID)' },
  'doc.guide': { es: 'Guía Explicativa', en: 'Explanatory Guide' },
  'doc.ready': { es: 'Listo', en: 'Ready' },
  'doc.pending': { es: 'Pendiente', en: 'Pending' },
  'doc.error': { es: 'Error', en: 'Error' },

  // Language toggle
  'lang.switch': { es: 'English', en: 'Español' },
  'lang.switch_icon': { es: '🇺🇸', en: '🇲🇽' },

  // Login
  'login.title': { es: 'Iniciar Sesión', en: 'Login' },
  'login.email': { es: 'Email', en: 'Email' },
  'login.password': { es: 'Contraseña', en: 'Password' },
  'login.submit': { es: 'Iniciar Sesión', en: 'Sign In' },
  'login.error': { es: 'Contraseña incorrecta', en: 'Incorrect password' },
  'login.rate_limited': { es: 'Demasiados intentos. Intenta de nuevo en 15 minutos.', en: 'Too many attempts. Try again in 15 minutes.' },
  'login.connection_error': { es: 'Error de conexión', en: 'Connection error' },
  'login.back': { es: '← Volver al sitio', en: '← Back to site' },
};

function getLocale(): 'es' | 'en' {
  const match = document.cookie.match(/tpt_lang=([^;]+)/);
  const val = match?.[1];
  if (val === 'en' || val === 'es') return val;
  return 'es';
}

function t(key: string, locale: 'es' | 'en'): string {
  return DICT[key]?.[locale] || key;
}

function translatePage() {
  const locale = getLocale();
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (key) {
      el.textContent = t(key, locale);
    }
  });
  // Update lang toggle button
  const toggleIcon = document.getElementById('lang-icon');
  const toggleLabel = document.getElementById('lang-label');
  if (toggleIcon) toggleIcon.textContent = t('lang.switch_icon', locale);
  if (toggleLabel) toggleLabel.textContent = t('lang.switch', locale);
}

// Run on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', translatePage);
} else {
  translatePage();
}

// Export helpers for dynamic content
(window as any).__i18n = { t, getLocale, DICT };
