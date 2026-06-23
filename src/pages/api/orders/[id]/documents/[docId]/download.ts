import type { APIRoute } from 'astro';
import { query } from '../../../../../../lib/db';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

/**
 * GET /api/orders/:orderId/documents/:docId/download
 *
 * Public endpoint (no auth) used by the customer panel at /panel.
 * Serves the generated PDF document if available on disk.
 * Returns a helpful message if the file hasn't been generated yet.
 */
export const GET: APIRoute = async (context) => {
  try {
    const { orderId, docId } = context.params;
    if (!orderId || !docId) {
      return new Response(JSON.stringify({ error: 'Order ID and Document ID required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Find document
    const docResult = await query(
      'SELECT * FROM documents WHERE id = $1 AND order_id = $2',
      [docId, orderId]
    );

    if (docResult.rows.length === 0) {
      return new Response(JSON.stringify({ error: 'Document not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const doc = docResult.rows[0];

    // If still being generated, return a clear message
    if (doc.status === 'generating' || doc.status === 'pending') {
      return new Response(JSON.stringify({
        error: 'Document is still being generated',
        status: doc.status,
        message: 'Este documento aún está en proceso. Intenta de nuevo en unos minutos.',
      }), {
        status: 202,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (doc.status !== 'ready' || !doc.file_path) {
      return new Response(JSON.stringify({ error: 'Document not available' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Check file exists on disk (ephemeral on Railway — may be missing after redeploy)
    if (!existsSync(doc.file_path)) {
      return new Response(JSON.stringify({
        error: 'Document file not found on disk',
        message: 'El archivo no está disponible en este momento. Contacta a soporte para recibir tu documento.',
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const fileBuffer = await readFile(doc.file_path);
    const fileName = doc.file_path.split('/').pop() || `document-${docId}.pdf`;

    return new Response(fileBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="${fileName}"`,
        'Content-Length': fileBuffer.length.toString(),
      },
    });
  } catch (e) {
    console.error('Error downloading document:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
