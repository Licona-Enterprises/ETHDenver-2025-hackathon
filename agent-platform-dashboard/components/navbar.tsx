"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { UserCircle } from "lucide-react"

const navItems = [
  { name: "Dashboard", href: "/" },
  { name: "Launch Agent", href: "/launch-agent" },
  { name: "My Agents", href: "/my-agents" },
  { name: "Train Agent", href: "/train-agent" },
]

export default function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="border-b">
      <div className="container mx-auto flex items-center justify-between p-4">
        <div className="flex items-center space-x-4">
          <Link href="/" className="text-2xl font-bold">
            AgentPlatform
          </Link>
          <div className="hidden md:flex space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  pathname === item.href ? "text-primary" : "text-muted-foreground",
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <UserCircle className="h-6 w-6" />
              <span className="sr-only">User menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem>Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </nav>
  )
}

