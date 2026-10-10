export type Decision = 'PASS' | 'FAIL' | 'REVIEW'
export interface Inspection {
  id: string; product: string; created_at: string; decision: Decision;
  anomaly_score: number | null; model_id: string; threshold_version: string;
  reasons: string[]; detections: unknown[]; latency_ms: number;
  image_url: string; overlay_url: string | null; review_status: string | null; review_note: string | null;
}

const json = async <T,>(responsePromise: Promise<Response>): Promise<T> => {
  const response = await responsePromise
  if (!response.ok) throw new Error((await response.json()).detail ?? `Request failed (${response.status})`)
  return response.json()
}
export const api = {
  health: () => json<{status:string;version:string}>(fetch('/api/health')),
  products: () => json<Record<string, unknown>>(fetch('/api/products')),
  models: () => json<Record<string, unknown>>(fetch('/api/models')),
  history: () => json<Inspection[]>(fetch('/api/inspections')),
  overview: () => json<{total:number, decisions:Record<string,number>}>(fetch('/api/analytics/overview')),
  inspect: (product: string, file: File) => {
    const body = new FormData(); body.append('product', product); body.append('file', file)
    return json<Inspection>(fetch('/api/inspections', { method: 'POST', body }))
  }
}
