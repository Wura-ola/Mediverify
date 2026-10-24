import React from "react";

export default function Nav() {
  return (
    <nav className="w-full bg-white border-b border-gray-100 py-4 px-6 md:px-12 flex items-center justify-between">
      {/* Left side: Logo and Navigation Links */}
      <div className="flex items-center space-x-12">
        {/* Logo Section */}
        <div className="flex items-center space-x-2 cursor-pointer">
          {/* Replace this div with your <img src="..." alt="Logo" /> if using an image file */}
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-sm">
            <span className="text-xs">MV</span>
          </div>
          <span className="text-xl font-bold text-gray-900 tracking-tight">
            MedVerify
          </span>
        </div>

        {/* Nav Links (Hidden on small screens) */}
        <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-gray-600">
          <a
            href="#how-it-works"
            className="hover:text-blue-600 transition-colors"
          >
            How it works
          </a>
          <a
            href="#for-hospitals"
            className="hover:text-blue-600 transition-colors"
          >
            For hospitals
          </a>
          <a
            href="#for-patients"
            className="hover:text-blue-600 transition-colors"
          >
            For patients
          </a>
        </div>
      </div>

      {/* Right side: Action Buttons */}
      <div className="hidden md:flex items-center space-x-4">
        <button className="text-sm font-medium text-gray-700 hover:text-blue-600 px-4 py-2 rounded-full transition-colors">
          Access my records
        </button>
        <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2.5 rounded-full shadow-sm transition-colors">
          For hospitals
        </button>
      </div>

      {/* Mobile Menu Hamburger Button */}
      <div className="md:hidden flex items-center">
        <button className="text-gray-700 focus:outline-none">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M4 6h16M4 12h16m-7 6h7"
            />
          </svg>
        </button>
      </div>
    </nav>
  );
}
