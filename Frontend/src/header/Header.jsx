import React from "react";

import Nav from "./nav/Nav";
import Hero from "./hero/Hero";

export default function Header() {
  return (
    <header className="w-full bg-white min-h-screen">
      <Nav />
      <Hero />
    </header>
  );
}
