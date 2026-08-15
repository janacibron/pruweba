const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_SECRET_KEY
);

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method Not Allowed' });

  try {
    const { name, email, bottleneck, revenue, notes } = req.body || {};

    if (!name || !email || !bottleneck) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const [{ error: auditError }, { error: trackError }] = await Promise.all([
      supabase.from('audit_requests').insert([
        { name, email, bottleneck, revenue: revenue || null, notes: notes || null },
      ]),
      supabase.from('tracking_events').insert([
        { event: 'lead_capture', target: 'audit_form', page: '/audit', domain: 'pruweba.com', timestamp: new Date().toISOString() },
      ]),
    ]);

    if (auditError) {
      console.error('Supabase audit insert failed:', auditError.message);
      return res.status(500).json({ error: 'Database error', details: auditError.message });
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('Audit error:', err);
    return res.status(500).json({ error: 'Internal Server Error' });
  }
};
