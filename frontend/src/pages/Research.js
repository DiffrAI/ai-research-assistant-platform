import React, { useState } from 'react';
import {
  Search,
  Loader2,
  Save,
  Download,
  ExternalLink,
  Copy,
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { researchAPI } from '../services/api';
import useAuthStore from '../store/authStore';

const Research = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [summary, setSummary] = useState('');
  const [citations, setCitations] = useState([]);
  const { user } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm();

  const query = watch('query');

  const onSubmit = async (data) => {
    setIsLoading(true);
    setResults(null);
    setSummary('');
    setCitations([]);

    try {
      const response = await researchAPI.conductResearch({
        query: data.query,
        max_results: parseInt(data.max_results) || 10,
        include_citations: true,
      });

      const researchData = response.data.data;
      setResults(researchData.results);
      setSummary(researchData.summary);
      setCitations(researchData.citations);

      toast.success('Research completed successfully!');
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Research failed';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!results) return;

    try {
      await researchAPI.saveResearch(
        {
          query,
          results,
          summary,
          citations,
        },
        ['research']
      );
      toast.success('Research saved successfully!');
    } catch (error) {
      toast.error('Failed to save research');
    }
  };

  const handleExport = async (format) => {
    if (!results) return;

    try {
      const response = await researchAPI.exportResearch({
        research_id: Date.now().toString(),
        format,
        query,
        results,
        summary,
      });

      // Create download link
      const blob = new Blob([response.data], {
        type: 'application/octet-stream',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `research_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Export failed');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            AI Research Assistant
          </h1>
          <p className="text-gray-600">
            Conduct intelligent research with AI-powered web search
          </p>
        </div>
        {user && (
          <div className="text-sm text-gray-500">
            Searches used: {user.searches_used_this_month}/{user.searches_limit}
          </div>
        )}
      </div>

      {/* Research Form */}
      <div className="card">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label
              htmlFor="query"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Research Query
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <textarea
                {...register('query', { required: 'Query is required' })}
                rows={3}
                className="input-field pl-10"
                placeholder="Enter your research question... (e.g., What are the latest developments in quantum computing?)"
              />
            </div>
            {errors.query && (
              <p className="mt-1 text-sm text-red-600">
                {errors.query.message}
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="max_results"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Max Results
              </label>
              <select
                {...register('max_results', { valueAsNumber: true })}
                className="input-field"
                defaultValue={10}
              >
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={15}>15 results</option>
                <option value={20}>20 results</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                Researching...
              </>
            ) : (
              <>
                <Search className="-ml-1 mr-3 h-5 w-5" />
                Start Research
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Summary */}
          {summary && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                AI Summary
              </h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed">{summary}</p>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleSave}
              className="btn-secondary flex items-center"
            >
              <Save className="mr-2 h-4 w-4" />
              Save Research
            </button>
            <button
              onClick={() => handleExport('pdf')}
              className="btn-secondary flex items-center"
            >
              <Download className="mr-2 h-4 w-4" />
              Export PDF
            </button>
            <button
              onClick={() => handleExport('markdown')}
              className="btn-secondary flex items-center"
            >
              <Download className="mr-2 h-4 w-4" />
              Export Markdown
            </button>
          </div>

          {/* Citations */}
          {citations.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Citations
              </h3>
              <div className="space-y-2">
                {citations.map((citation, index) => (
                  <div
                    key={index}
                    className="flex items-start justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <span className="text-sm text-gray-700">{citation}</span>
                    <button
                      onClick={() => copyToClipboard(citation)}
                      className="ml-2 text-gray-400 hover:text-gray-600"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Search Results */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Search Results ({results.length})
            </h3>
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-2">
                        {result.title}
                      </h4>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                        {result.content}
                      </p>
                      <div className="flex items-center text-xs text-gray-500">
                        <span className="mr-4">Source: {result.source}</span>
                        {result.relevance_score && (
                          <span>
                            Relevance:{' '}
                            {Math.round(result.relevance_score * 100)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Research;
