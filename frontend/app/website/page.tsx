'use client'

import Link from 'next/link'
import ProtectedRoute from '@/components/ProtectedRoute'
import Sidebar from '@/components/Sidebar'
import { Globe, Image, Mail, CalendarDays, MapPin } from 'lucide-react'

const cards = [
  { href: '/website/content', title: 'Showcase / content', text: 'Hero slides, about, gallery, blog, venue copy', icon: Image },
  { href: '/website/bookings', title: 'Website bookings', text: 'Reservations and dining orders from the public site', icon: CalendarDays },
  { href: '/website/contacts', title: 'Contact inbox', text: 'Messages sent from the landing contact form', icon: Mail },
  { href: '/frontdesk/config/room-types', title: 'Rooms catalog', text: 'Room types shown on Accommodations', icon: MapPin },
  { href: '/site/turag', title: 'Live site', text: 'Open the public website', icon: Globe },
]

export default function WebsiteHubPage() {
  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-200">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-y-auto p-6">
          <h1 className="text-3xl font-bold text-gray-900">Website</h1>
          <p className="mt-1 text-gray-600">
            Same modules as the Turag public site: showcase, rooms, activities, gallery, blog, venue, booking, and contact.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {cards.map((c) => (
              <Link
                key={c.href + c.title}
                href={c.href}
                className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:border-indigo-200"
              >
                <c.icon className="h-6 w-6 text-indigo-600" />
                <h2 className="mt-3 font-semibold text-gray-900">{c.title}</h2>
                <p className="mt-1 text-sm text-gray-600">{c.text}</p>
              </Link>
            ))}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
