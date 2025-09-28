import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { lat = 10, lon = -45, radius = 200 } = req.query;

  const url = `https://argovis.colorado.edu/catalog/profiles?lat=${lat}&lon=${lon}&radius=${radius}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': 'Bearer ' + (process.env.ARGOVIS_API_KEY || '')
      }
    });
    const data = await response.json();
    res.status(200).json(data);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
}
