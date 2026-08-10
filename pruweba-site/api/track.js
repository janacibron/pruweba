const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method Not Allowed' });

  try {
    const { event, target, page, domain, timestamp } = req.body || {};

    if (!event || !target || !page || !domain || !timestamp) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const { error } = await supabase
      .from('tracking_events')
      .insert([{ event, target, page, domain, timestamp }]);

    if (error) {
      console.error('Supabase insert failed:', error.message);
      return res.status(200).json({ ok: true, stored: false, reason: 'supabase_insert_failed' });
    }

    return res.status(200).json({ ok: true, stored: true });
  } catch (err) {
    console.error('Track error:', err);
    return res.status(500).json({ error: 'Internal Server Error' });
  }
};
