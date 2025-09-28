"use client"
import "leaflet/dist/leaflet.css"
import { MapContainer, TileLayer, useMapEvents, CircleMarker } from "react-leaflet"
import { useState } from "react"
import type { LatLng, LatLngExpression, LeafletMouseEvent } from "leaflet"

function LocationMarker({ onSelect }: { onSelect: (latlng: LatLng) => void }) {
  const [pos, setPos] = useState<LatLng | null>(null)
  useMapEvents({
    click(e: LeafletMouseEvent) {
      setPos(e.latlng)
      onSelect(e.latlng)
    }
  })
  return pos ? <CircleMarker center={pos as LatLngExpression} radius={6} pathOptions={{ color: "red" }} /> : null
}

export default function OceanMap({ onRegionSelect }: { onRegionSelect: (coords: LatLng) => void }) {
  const initialCenter: LatLngExpression = [0, 0]
  return (
    <div className="rounded-lg overflow-hidden shadow">
      <MapContainer center={initialCenter} zoom={2} className="h-96 w-full">
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker onSelect={onRegionSelect} />
      </MapContainer>
    </div>
  )
}
