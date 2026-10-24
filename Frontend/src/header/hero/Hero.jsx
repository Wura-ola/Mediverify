import React from "react";

export default function Hero() {
  return (
    <section className="w-full bg-gradient-to-b from-white to-blue-50/40 py-12 md:py-20 px-6 md:px-12 flex items-center">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center w-full">
        {/* Left Column: Text & Buttons (Cols 1-6) */}
        <div className="lg:col-span-6 flex flex-col items-start space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 text-xs font-semibold px-3 py-1.5 rounded-md border border-blue-100">
            <svg
              className="w-3.5 h-3.5 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>CONNECTED MEDICAL RECORDS</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-gray-900 tracking-tight leading-[1.1]">
            Your medical history should travel with you.
          </h1>

          {/* Subtitle description */}
          <p className="text-lg text-gray-600 max-w-lg leading-relaxed">
            MedVerify connects hospital-managed medical records with the
            patients who need to carry them across healthcare facilities.
          </p>

          {/* Action CTA Buttons */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-xl shadow-md transition-all flex items-center space-x-2">
              <span>For hospitals</span>
            </button>
            <button className="bg-white hover:bg-gray-50 text-gray-800 border border-gray-200 font-medium px-6 py-3 rounded-xl shadow-sm transition-all flex items-center space-x-2">
              <span>Access my records</span>
            </button>
          </div>
        </div>

        {/* Right Column: Space for your Image/Graphic (Cols 7-12) */}
        <div className="lg:col-span-6 w-full flex justify-center">
          {/* 
            TODO: Replace this container with your image. 
            Example: <img src="/your-dashboard-graphic.png" alt="Dashboard" className="w-full h-auto object-contain rounded-2xl shadow-xl border border-gray-100" />
          */}
          <div className="w-full aspect-[4/3] bg-white border border-gray-200/80 rounded-2xl shadow-xl p-6 flex flex-col justify-between relative overflow-hidden">
            {/* Top row of the dashboard mockup */}
            <div className="flex justify-between items-center border-b border-gray-100 pb-4">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-xs font-bold text-gray-700 tracking-wider">
                  FEDERATED RECORD INTERCHANGE
                </span>
              </div>
              <span className="text-xs bg-gray-100 text-gray-600 font-medium px-2.5 py-1 rounded-md">
                Node Active
              </span>
            </div>

            {/* Inner Cards representation matching the screenshot */}
            <div className="grid grid-cols-2 gap-4 my-auto py-4">
              <div className="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mb-2">
                  🏥
                </div>
                <div className="text-xs font-bold text-gray-800">
                  Hospital record
                </div>
                <div className="text-[10px] text-gray-500">
                  Metropolitan Health
                </div>
              </div>
              <div className="border-2 border-blue-600 rounded-xl p-4 bg-white shadow-sm relative">
                <span className="absolute -top-2.5 right-3 bg-blue-900 text-white text-[9px] px-2 py-0.5 rounded-full font-bold">
                  Hub
                </span>
                <div className="w-8 h-8 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mb-2">
                  🛡️
                </div>
                <div className="text-xs font-bold text-gray-900">MedVerify</div>
                <div className="text-[10px] text-blue-600 font-medium">
                  Connected records
                </div>
              </div>
            </div>

            {/* Bottom info of mockup */}
            <div className="border-t border-gray-100 pt-3 flex justify-between items-center text-[11px] text-gray-500 font-medium">
              <span>Portability across facilities without fragmentation</span>
              <span className="text-gray-400 font-mono text-[10px]">
                ZERO RE-ENTRY
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
