import React, { useState } from "react";
import { searchEmployeesByName, EmployeeSearchResult } from "../api/employeeApi";

const EmployeeSearchPage: React.FC = () => {
  const [searchFirstName, setSearchFirstName] = useState("");
  const [searchLastName, setSearchLastName] = useState("");
  const [searchResults, setSearchResults] = useState<EmployeeSearchResult[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searching, setSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (page: number = 1) => {
    if (!searchFirstName && !searchLastName) {
      return;
    }

    try {
      setSearching(true);
      setHasSearched(true);
      const results = await searchEmployeesByName(searchFirstName, searchLastName, page);
      setSearchResults(results);
      setCurrentPage(page);
    } catch (err) {
      console.error("Search failed:", err);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch(1);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Employee Search</h1>
        <p className="text-gray-600 mt-1">Search for employees by first or last name</p>
      </div>

      {/* Search Card */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Search Employees</h2>
            <p className="text-sm text-gray-500">Enter first name, last name, or both</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              First Name
            </label>
            <input
              type="text"
              value={searchFirstName}
              onChange={(e) => setSearchFirstName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., Alex"
              className="input-field"
              disabled={searching}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Last Name
            </label>
            <input
              type="text"
              value={searchLastName}
              onChange={(e) => setSearchLastName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., Smith"
              className="input-field"
              disabled={searching}
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={() => handleSearch(1)}
              disabled={searching || (!searchFirstName && !searchLastName)}
              className="btn-primary w-full"
            >
              {searching ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                "Search"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Results Card */}
      {hasSearched && (
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Search Results</h2>
              <p className="text-sm text-gray-500">
                {searchResults.length} {searchResults.length === 1 ? "employee" : "employees"} found
              </p>
            </div>
          </div>

          {searchResults.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Employee No</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">First Name</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Last Name</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Gender</th>
                    </tr>
                  </thead>
                  <tbody>
                    {searchResults.map((emp, idx) => (
                      <tr key={emp.emp_no} className={idx % 2 === 0 ? "bg-gray-50" : ""}>
                        <td className="py-3 px-4 text-sm text-gray-900 font-medium">{emp.emp_no}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{emp.first_name}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{emp.last_name}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{emp.gender}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleSearch(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1 || searching}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg className="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Previous
                </button>
                
                <div className="text-sm text-gray-600 font-medium">
                  Page {currentPage}
                </div>

                <button
                  onClick={() => handleSearch(currentPage + 1)}
                  disabled={searchResults.length < 10 || searching}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                  <svg className="w-5 h-5 ml-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>

              <p className="text-xs text-gray-500 mt-4 text-center">
                Showing up to 10 results per page
              </p>
            </>
          ) : (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-500 text-lg font-medium">No employees found</p>
              <p className="text-gray-400 text-sm mt-2">Try adjusting your search criteria</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmployeeSearchPage;
