'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Compass,
  MapPin,
  Trees,
  FlaskConical,
  QrCode,
  ClipboardList,
  RefreshCw,
} from 'lucide-react';
import { syncService } from '@/lib/syncService';

export default function Navigation() {
  const pathname = usePathname();
  const [pendingCount, setPendingCount] = useState<number>(0);

  useEffect(() => {
    const checkCount = async () => {
      try {
        const counts = await syncService.countPendingItems();
        setPendingCount(counts.total);
      } catch {}
    };
    checkCount();
    const interval = setInterval(checkCount, 3000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { label: 'Accueil', href: '/', icon: Compass },
    { label: 'Placettes', href: '/plots', icon: MapPin },
    { label: 'Arbres', href: '/inventory', icon: Trees },
    { label: 'Traits Lab', href: '/traits', icon: FlaskConical },
    { label: 'QR-Codes', href: '/qrcode', icon: QrCode },
    { label: 'Enquêtes', href: '/surveys', icon: ClipboardList },
    {
      label: 'Sync',
      href: '/sync',
      icon: RefreshCw,
      badge: pendingCount > 0 ? pendingCount : undefined,
    },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-zinc-950/95 border-t border-savanna-900 backdrop-blur-md safe-bottom">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto px-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`relative flex flex-col items-center justify-center flex-1 py-1 transition-colors ${
                isActive
                  ? 'text-emerald-400 font-semibold'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <div className="relative">
                <Icon
                  className={`w-5 h-5 transition-transform ${
                    isActive ? 'scale-110 stroke-[2.5]' : 'stroke-[1.8]'
                  }`}
                />
                {item.badge !== undefined && (
                  <span className="absolute -top-1.5 -right-2 bg-sahel-500 text-black text-[10px] font-black rounded-full w-4 h-4 flex items-center justify-center animate-bounce">
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </div>
              <span className="text-[10px] mt-1 tracking-tight truncate max-w-[54px]">
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
