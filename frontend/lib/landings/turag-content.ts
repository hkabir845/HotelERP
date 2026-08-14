export type LandingNavItem = { id: string; label: string }
export type LandingHighlight = { title: string; text: string }
export type LandingStay = { key: string; name: string; blurb: string; image: string }
export type LandingActivity = { name: string; text: string }
export type LandingGalleryItem = { src: string; alt: string; type?: string }
export type LandingBlogPost = { title: string; slug: string; excerpt: string; date: string }

export type LandingContent = {
  brand: string
  tagline: string
  shortPitch: string
  about: { title: string; body: string; eco: string; boutique: string }
  highlights: LandingHighlight[]
  accommodations: LandingStay[]
  activities: LandingActivity[]
  contact: {
    resortAddress: string
    dhakaOffice: string
    emails: string[]
    phones: string[]
    website: string
    facebook: string
  }
  images: {
    logo: string
    hero: string
    about: string
    cottage: string
    pool: string
    dining: string
    nature: string
  }
  heroSlides: LandingGalleryItem[]
  gallery: LandingGalleryItem[]
  blog: LandingBlogPost[]
  nav: LandingNavItem[]
  copy: {
    heroLocation: string
    heroPhones: string
    aboutCaption: string
    stayEyebrow: string
    stayTitle: string
    stayIntro: string
    activitiesEyebrow: string
    activitiesTitle: string
    activitiesIntro: string
    galleryEyebrow: string
    galleryTitle: string
    galleryIntro: string
    blogEyebrow: string
    blogTitle: string
    venueEyebrow: string
    venueTitle: string
    contactFormTitle: string
    ecoTitle: string
    boutiqueTitle: string
    ctaBook: string
    ctaOrder: string
    ctaDiscover: string
    ctaReserve: string
    liveSite: string
    facebook: string
    staffLogin: string
    footerNote: string
  }
}

export const DEFAULT_TURAG_CONTENT: LandingContent = {
  brand: 'Turag Waterfront Resort',
  tagline: 'Where Nature Meets Comfort. Experience Peace & Adventure at the Best Resort in Gazipur.',
  shortPitch:
    'A peaceful retreat by the Turag River on 36 bighas of land, near Bhawal National Park — cozy wooden cottages, open-air dining, a large swimming pool, and riverside adventure.',
  about: {
    title: 'About Turag Waterfront Resort',
    body:
      'Turag Waterfront Resort in Gazipur, Dhaka, is located 18KM from Gazipur Bypass. Surrounded by lush greenery and serene river views, it is the perfect escape from city life. Founded by Md. Humayun Kabir and Shahin Alambir, the resort preserves the traditional riverside lifestyle while providing an eco-friendly and tranquil environment for families, corporate retreats, and romantic getaways.',
    eco:
      'As an eco-friendly boutique resort we focus on energy saving, limiting water waste, linen reuse, eco-conscious cleaning, local and organic food, and composting — giving back to our community while protecting the river landscape.',
    boutique:
      'Our ~50-room boutique resort offers vibrant landscaping and modern amenities. From the moment of arrival, guests feel embraced by nature.',
  },
  highlights: [
    { title: 'Couples & families', text: 'A calm riverside setting made for shared moments.' },
    { title: 'Corporate & workshops', text: 'Gazipur venue space for meetings and retreats.' },
    { title: 'Cottages & suites', text: 'River-view wooden cottages and comfortable suites.' },
    { title: 'Restaurant dining', text: 'Open-air dining with delicious local and modern dishes.' },
  ],
  accommodations: [
    {
      key: 'deluxe',
      name: 'Deluxe',
      blurb: 'Comfortable rooms with modern amenities for a restful stay.',
      image: '/landings/turag/deluxe.jpg',
    },
    {
      key: 'cottage',
      name: 'Cottage',
      blurb: 'Cozy wooden cottages — wake to fresh air and the sound of flowing water.',
      image: '/landings/turag/lakeview.jpg',
    },
    {
      key: 'suite',
      name: 'Suite',
      blurb: 'Spacious suites for families and longer escapes.',
      image: '/landings/turag/exclusive_deluxe.png',
    },
    {
      key: 'villa',
      name: 'Villa',
      blurb: 'Private villa-style stays with room to breathe.',
      image: '/landings/turag/villa.jpg',
    },
    {
      key: 'platinum',
      name: 'Platinum',
      blurb: 'Premium riverside living for unforgettable occasions.',
      image: '/landings/turag/platinum.jpg',
    },
  ],
  activities: [
    { name: 'Boating', text: 'Glide along the Turag River at your own pace.' },
    { name: 'Fishing', text: 'Quiet riverside fishing in a natural setting.' },
    { name: 'Swimming pool', text: 'A large pool for cooling off under open skies.' },
    { name: 'Indoor games', text: 'Games and recreation for rainy afternoons.' },
    { name: "Kids' play zone", text: 'Safe outdoor play space for little guests.' },
    { name: 'Nature walks', text: 'Lush greenery near Bhawal National Park.' },
  ],
  contact: {
    resortAddress: 'Mouchak-Fulbaria Road, Chabagan Bazar, Kaliakoir, Gazipur',
    dhakaOffice: '2nd Floor, House-34, Road-2, Nikunja-2, Khilkhet, Dhaka-1229',
    emails: ['contact@turagwaterfrontresort.com', 'turagwaterfrontresortltd@gmail.com'],
    phones: ['+880 1970-863933', '01332-848177', '01332-848174', '01332-848168', '01970-863934'],
    website: 'https://turag.sascorporationbd.com',
    facebook: 'https://www.facebook.com/turagwaterfrontresort',
  },
  images: {
    logo: '/landings/turag/logo.png?v=4',
    hero: '/landings/turag/hero.png?v=2',
    about: '/landings/turag/home-gazipur.jpeg',
    cottage: '/landings/turag/lakeview.jpg',
    pool: '/landings/turag/pool.jpg',
    dining: '/landings/turag/dining.jpeg',
    nature: '/landings/turag/boating.jpeg',
  },
  heroSlides: [
    {
      src: '/landings/turag/hero.png?v=2',
      alt: 'Turag Waterfront Resort lawn, river bridges, and red boat',
    },
    {
      src: '/landings/turag/home-gazipur.jpeg',
      alt: 'Aerial view of overwater cottages on the Turag River',
    },
    {
      src: '/landings/turag/home-resort2.png',
      alt: 'Aerial view of the resort canal, lawn, and cottages',
    },
  ],
  gallery: [
    { src: '/landings/turag/home-gazipur.jpeg', alt: 'Aerial view of overwater cottages on the Turag River', type: 'Outdoor' },
    { src: '/landings/turag/home-book-cover.jpg', alt: 'Colorful river cottages from the wooden deck', type: 'Rooms' },
    { src: '/landings/turag/home-resort3.jpg', alt: 'Rainbow wooden bridge over the water', type: 'Outdoor' },
    { src: '/landings/turag/pool.jpg', alt: 'Swimming pool at Turag Waterfront Resort', type: 'Outdoor' },
    { src: '/landings/turag/walkway.jpeg', alt: 'Boardwalk to the teal-roof cottage', type: 'Outdoor' },
    { src: '/landings/turag/boating.jpeg', alt: 'River view and red boat from a cottage deck', type: 'Activities' },
    { src: '/landings/turag/night.jpeg', alt: 'Night lights reflecting on the river', type: 'Outdoor' },
    { src: '/landings/turag/home-info2.jpeg', alt: 'Night walkway with colored globe lights', type: 'Outdoor' },
    { src: '/landings/turag/outdoor-dining.jpg', alt: 'Open-air dining pavilion and garden', type: 'Dining' },
    { src: '/landings/turag/bbq.jpg', alt: 'BBQ gathering at the Gazipur resort', type: 'Dining' },
    { src: '/landings/turag/kayaking.jpeg', alt: 'Kayaking on the resort pond', type: 'Activities' },
    { src: '/landings/turag/platinum.jpg', alt: 'Platinum house balcony overlooking the river', type: 'Rooms' },
  ],
  blog: [
    {
      title: 'A weekend by the Turag River',
      slug: 'weekend-by-the-turag',
      excerpt: 'Wooden cottages, slow boats, and open-air dining — how guests spend a Gazipur getaway.',
      date: '2026-03-12',
    },
    {
      title: 'Eco-friendly stays in Mouchak',
      slug: 'eco-friendly-mouchak',
      excerpt: 'Energy saving, linen reuse, and local food — the boutique resort’s nature-first habits.',
      date: '2026-01-20',
    },
  ],
  nav: [
    { id: 'home', label: 'Home' },
    { id: 'about', label: 'About' },
    { id: 'stay', label: 'Accommodations' },
    { id: 'activities', label: 'Activities' },
    { id: 'gallery', label: 'Gallery' },
    { id: 'blog', label: 'Blog' },
    { id: 'venue', label: 'Gazipur Venue' },
    { id: 'contact', label: 'Contact' },
  ],
  copy: {
    heroLocation: 'Mouchak, Gazipur · A resort by nature',
    heroPhones: '01970-863933 · 01730-863933',
    aboutCaption: 'Nature meets comfort on the banks of the Turag',
    stayEyebrow: 'Pinnacle of Comfort',
    stayTitle: 'Accommodations',
    stayIntro:
      'Stay close to nature while enjoying modern comforts — from river-view wooden cottages to premium platinum stays.',
    activitiesEyebrow: 'Pinnacle of Happiness',
    activitiesTitle: 'Activities',
    activitiesIntro:
      "Boating, fishing, swimming, indoor games, and a kids' play zone — adventure and calm in one riverside estate.",
    galleryEyebrow: 'From the grounds',
    galleryTitle: 'Gallery',
    galleryIntro:
      'Real photographs of Turag Waterfront Resort — cottages, river, pool, dining, and night lights.',
    blogEyebrow: 'From the resort',
    blogTitle: 'Blog',
    venueEyebrow: 'Pinnacle of Comfort',
    venueTitle: 'Gazipur Venue',
    contactFormTitle: 'Send a message',
    ecoTitle: 'Eco-friendly',
    boutiqueTitle: 'Boutique resort',
    ctaBook: 'Book Now',
    ctaOrder: 'Order dining',
    ctaDiscover: 'Discover more',
    ctaReserve: 'Reserve →',
    liveSite: 'Live site',
    facebook: 'Facebook',
    staffLogin: 'Staff login',
    footerNote: 'All rights reserved.',
  },
}

/** @deprecated use DEFAULT_TURAG_CONTENT */
export const TURAG_CONTENT = DEFAULT_TURAG_CONTENT

function isObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value)
}

export function deepMerge<T>(base: T, override: unknown): T {
  if (override === undefined || override === null) return base
  if (Array.isArray(override)) return override as T
  if (!isObject(base) || !isObject(override)) return override as T
  const out: Record<string, unknown> = { ...(base as Record<string, unknown>) }
  for (const [key, value] of Object.entries(override)) {
    if (value === undefined) continue
    out[key] = deepMerge((base as Record<string, unknown>)[key], value)
  }
  return out as T
}

export function mergeLandingContent(override?: unknown | null): LandingContent {
  const merged = deepMerge(DEFAULT_TURAG_CONTENT, override || {})
  if (!merged.heroSlides?.length) {
    merged.heroSlides = DEFAULT_TURAG_CONTENT.heroSlides
  }
  if (!merged.blog?.length) {
    merged.blog = DEFAULT_TURAG_CONTENT.blog
  }
  return merged
}
