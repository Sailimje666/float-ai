'use client'
import { useEffect, useState } from 'react';

export default function ArgovisData() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/argovis?lat=10&lon=-45&radius=200', { cache: 'no-store' })
      .then(res => res.json())
      .then(json => setData(json?.floats ?? []));
  }, []);

  return (
    <div>
      <h2>Argovis Data</h2>
      <pre>{JSON.stringify(data.slice(0,5), null, 2)}</pre>
    </div>
  );
}
