# Agent Forge Website

The official website for Agent Forge - a production-ready Python framework for AI agents with built-in browser automation and MCP integration.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 🏗️ Built With

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible components
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons

## 🎨 Design System

The website implements the Agent Forge brand identity:

### Colors
- **Ancient Gold**: `#F59E0B` - Primary actions and highlights
- **Nuru Purple**: `#7C3AED` - Secondary actions and links
- **Ancient Bronze**: `#CD7F32` - Accents and decorative elements
- **Charcoal Anvil**: `#36454F` - Text and dark backgrounds
- **Forge White**: `#FEFEFE` - Clean backgrounds

### Typography
- **Primary**: Inter font family
- **Code**: JetBrains Mono font family

### Animations
- **Forge Glow**: Subtle pulse animation on primary elements
- **Ancient Fade**: Gentle opacity transitions
- **Ember Float**: Floating particle effects

## 📁 Project Structure

```
website/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx           # Homepage
│   │   ├── docs/              # Documentation pages
│   │   └── examples/          # Examples showcase
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── layout/            # Layout components
│   │   └── home/              # Homepage sections
│   ├── lib/
│   │   └── utils.ts           # Utility functions
│   └── styles/
│       └── globals.css        # Global styles
├── public/                    # Static assets
├── tailwind.config.ts         # Tailwind configuration
└── next.config.ts            # Next.js configuration
```

## 🎯 Key Features

### Homepage
- **Hero Section**: Compelling introduction with animated elements
- **Features Section**: Key benefits and capabilities
- **Framework Overview**: Code examples and use cases
- **CTA Section**: Clear calls-to-action for getting started

### Documentation
- **Getting Started**: Step-by-step installation and first agent
- **Examples**: Working code examples with copy functionality
- **API Reference**: Comprehensive technical documentation

### Design
- **Responsive**: Mobile-first design optimized for all devices
- **Accessible**: WCAG 2.1 AA compliant with proper semantics
- **Performance**: Optimized for Core Web Vitals and Lighthouse scores
- **Brand Consistent**: Implements Agent Forge visual identity throughout

## 🚀 Deployment

The website is optimized for deployment on Vercel:

```bash
# Build and export for static hosting
npm run build

# The build output is ready for deployment
```

### Environment Variables

No environment variables are required for the basic website functionality.

## 📊 Performance

The website is optimized for:
- **Core Web Vitals**: LCP <2.5s, FID <100ms, CLS <0.1
- **Lighthouse Score**: 95+ across all categories
- **Bundle Size**: <500KB initial load
- **SEO**: Structured data and meta tags for search optimization

## 🤝 Contributing

1. Follow the existing code style and component patterns
2. Use TypeScript for all new components
3. Ensure accessibility compliance
4. Test responsive design across device sizes
5. Maintain brand consistency with design system

## 📝 License

This website is part of the Agent Forge project. See the main project LICENSE for details.

---

**Built with ancient wisdom and modern technology 🔥**
