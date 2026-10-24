import React from "react";

export default function Hero() {
  return (
    <section className="w-full bg-[#f2f7fd] py-16 px-6 md:px-16 min-h-[calc(100vh-73px)] flex items-center">
      <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        {/* Left Content Column */}
        <div className="lg:col-span-6 flex flex-col items-start space-y-6">
          {/* Badge Tag */}
          <div className="inline-flex items-center space-x-2 bg-[#e6f0fa] border border-[#d0e3f7] text-[#0062d2] px-3 py-1 rounded-md text-xs font-bold tracking-wide uppercase">
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth="2.5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>CONNECTED MEDICAL RECORDS</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-[56px] font-extrabold text-[#0c1e3c] leading-[1.1] tracking-tight">
            Your medical history should travel with you.
          </h1>

          {/* Subheading */}
          <p className="text-base sm:text-lg text-gray-600 max-w-lg leading-relaxed">
            MedVerify connects hospital-managed medical records with the
            patients who need to carry them across healthcare facilities.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button className="bg-[#0062d2] hover:bg-blue-700 text-white font-semibold text-sm px-6 py-3.5 rounded-xl shadow-md transition-all flex items-center space-x-2">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                />
              </svg>
              <span>For hospitals</span>
            </button>

            <button className="bg-white hover:bg-gray-50 text-gray-800 border border-gray-200/80 font-semibold text-sm px-6 py-3.5 rounded-xl shadow-sm transition-all flex items-center space-x-2">
              <svg
                className="w-4 h-4 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 012-2h2a2 2 0 012 2v1m-6 0h6"
                />
              </svg>
              <span>Access my records</span>
            </button>
          </div>
        </div>

        {/* Right Graphic Space (Image Container) */}
        <div className="lg:col-span-6 w-full flex justify-center">
          {/*
            To use your image, simply uncomment this:
            <img src="/your-image-path.png" alt="MedVerify Diagram" className="w-full h-auto max-w-xl object-contain rounded-3xl shadow-xl" />
          */}

          {/* Interactive UI Card Graphic replica matching screenshot */}
          <div className="w-full max-w-xl bg-white/90 backdrop-blur-md border border-white/60 rounded-3xl p-6 sm:p-8 shadow-[0_20px_50px_rgba(0,0,0,0.06)] relative flex flex-col justify-between">
            {/* Top Bar inside diagram */}
            <div className="flex justify-between items-center pb-6 border-b border-gray-100">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 bg-emerald-500 rounded-full"></span>
                <span className="text-xs font-bold tracking-wider text-[#0062d2]">
                  FEDERATED RECORD INTERCHANGE
                </span>
              </div>
              <span className="text-xs bg-gray-100 text-gray-500 font-semibold px-3 py-1 rounded-full">
                Node Active
              </span>
            </div>

            {/* 2x2 Grid Section */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-6">
              {/* Card 1: Hospital Record */}
              <div className="border border-gray-200/80 rounded-2xl p-4 bg-white shadow-sm flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <div className="p-2 bg-blue-50 text-blue-600 rounded-xl mb-3">
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      strokeWidth="2"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-gray-900">
                    Hospital record
                  </h4>
                  <p className="text-xs text-gray-500">Metropolitan Health</p>
                </div>
                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-700">
                    Origin verified
                  </span>
                  <svg
                    className="w-4 h-4 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth="2.5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
              </div>

              {/* Card 2: MedVerify Active Hub (Highlighted) */}
              <div className="border-2 border-[#0062d2] rounded-2xl p-4 bg-white shadow-md relative flex flex-col justify-between">
                <span className="absolute -top-3 right-4 bg-[#0062d2] text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full">
                  Hub
                </span>
                <div className="flex flex-col items-center text-center my-auto py-2">
                  <div className="p-2.5 bg-blue-50 text-blue-600 rounded-full mb-2">
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      strokeWidth="2"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                      />
                    </svg>
                  </div>
                  <h4 className="text-sm font-extrabold text-[#0c1e3c]">
                    MedVerify
                  </h4>
                  <span className="text-xs bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded-md font-medium mt-1">
                    Connected records
                  </span>
                  <span className="text-[11px] text-gray-500 font-medium mt-3">
                    Immutable Audit Sync
                  </span>
                </div>
              </div>

              {/* Card 3: Patient Access */}
              <div className="border border-gray-200/80 rounded-2xl p-4 bg-white shadow-sm flex flex-col justify-between">
                <div className="p-2 bg-blue-50 text-blue-600 rounded-xl w-fit mb-3">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth="2"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-gray-900">
                    Patient access
                  </h4>
                  <p className="text-xs text-gray-500">ID: MV-20481</p>
                </div>
                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center space-x-1.5 text-emerald-600 text-xs font-semibold">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth="2.5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span>Medical history at hand</span>
                </div>
              </div>

              {/* Card 4: External Facility */}
              <div className="border border-gray-200/80 rounded-2xl p-4 bg-white shadow-sm flex flex-col justify-between">
                <div className="p-2 bg-blue-50 text-blue-600 rounded-xl w-fit mb-3">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth="2"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5"
                    />
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-gray-900">
                    External facility
                  </h4>
                  <p className="text-xs text-gray-500">Receiving Point</p>
                </div>
                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500 font-medium">
                  <span>Intake sync</span>
                  <span className="text-gray-900 font-semibold">Ready</span>
                </div>
              </div>
            </div>

            {/* Bottom Footer Row inside graphic */}
            <div className="pt-4 border-t border-gray-100 flex items-center justify-between text-[11px] font-semibold text-gray-500">
              <span className="flex items-center space-x-1">
                <span>
                  ⇆ Portability across facilities without fragmentation
                </span>
              </span>
              <span className="tracking-wider uppercase text-gray-400">
                ZERO RE-ENTRY
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
