import React from "react";

export default function Nav() {
  return (
    <nav className="w-full bg-white px-6 md:px-16 py-4 flex items-center justify-between border-b border-gray-100">
      {/* Brand Logo & Nav Links */}
      <div className="flex items-center space-x-10">
        {/* Logo */}
        <a href="#" className="flex items-center space-x-2.5 group">
          <div className="text-blue-600">
            {/* Custom MedVerify Icon matching image */}
            <svg
              className="w-7 h-7"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <path d="m9 15 2 2 4-4" />
            </svg>
          </div>
          <span className="text-xl font-bold text-[#0c1e3c] tracking-tight">
            MedVerify
          </span>
        </a>

        {/* Navigation Links */}
        <div className="hidden md:flex items-center space-x-7 text-sm font-medium text-gray-600">
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

      {/* Action Buttons */}
      <div className="hidden md:flex items-center space-x-3">
        <button className="text-sm font-semibold text-gray-700 hover:text-blue-600 px-4 py-2 transition-colors">
          Access my records
        </button>
        <button className="bg-[#0062d2] hover:bg-blue-700 text-white text-sm font-semibold px-5 py-2.5 rounded-2xl shadow-sm transition-all">
          For hospitals
        </button>
      </div>
    </nav>
  );
}
