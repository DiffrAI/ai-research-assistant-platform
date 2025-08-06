import React, { useState, useCallback, useRef } from 'react';
import {
  Search,
  Save,
  Download,
  ExternalLink,
  Copy,
  Filter,
  BookOpen,
  History,
  Sparkles,
  Clock,
  TrendingUp,
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { researchAPI } from '../services/api';
import useAuthStore from '../store/authStore';
import { useApi } from '../hooks/useApi';
import { Button, Input, Card, Modal } from '../components/ui';
import SearchHistory from '../components/SearchHistory';
import type { SearchResult } from '../types';
import { copyToClipboard } from '../utils/helpers';

interface FormData {
  query: string;
  max_results: number;
}

const Research: React.FC = () => {
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [summary, setSummary] = useState<string>('');
  const [citations, setCitations] = useState<string[]>([]);
  const [showSaveModal, setShowSaveModal] = useState<boolean>(false);
  const [showHistoryModal, setShowHistoryModal] = useState<boolean>(false);
  const [saveTitle, setSaveTitle] = useState<string>('');
  const [saveTags, setSaveTags] = useState<string>('');
  const [searchStartTime, setSearchStartTime] = useState<number | null>(null);
  const [searchDuration, setSearchDuration] = useState<number | null>(null);
  const { user } = useAuthStore();
  const { loading: isLoading, execute } = useApi();
  const searchHistoryRef = useRef<{ addToHistory: (query: string, resultsCount?: number) => void }>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<FormData>({
    defaultValues: {
      max_results: 10,
    },
  });

  const query = watch('query');

  const onSubmit = useCallback(async (data: FormData) => {
    setResults(null);
    setSummary('');
    setCitations([]);
    setSearchStartTime(Date.now());
    setSearchDuration(null);

    await execute(
      () => researchAPI.conductResearch({
        query: data.query,
        max_results: parseInt(data.max_results.toString()) || 10,
        include_citations: true,
      }),
      {
        onSuccess: (response) => {
          const researchData = response.data.data;
          setResults(researchData.results);
          setSummary(researchData.summary);
          setCitations(researchData.citations);
          setSaveTitle(data.query); // Auto-populate save title
          
          // Calculate search duration
          if (searchStartTime) {
            setSearchDuration(Date.now() - searchStartTime);
          }
          
          // Add to search history
          if (searchHistoryRef.current) {
            searchHistoryRef.current.addToHistory(data.query, researchData.results.length);
          }
        },
        showSuccessToast: true,
        successMessage: 'Research completed successfully!',
      }
    );
  }, [execute, searchStartTime]);

  const handleSave = useCallback(async () => {
    if (!results) return;

    const tags = saveTags.split(',').map(tag => tag.trim()).filter(Boolean);
    
    await execute(
      () => researchAPI.saveResearch(
        {
          title: saveTitle || query,
          query,
          results,
          summary,
          citations,
        },
        tags.length > 0 ? tags : ['research']
      ),
      {
        showSuccessToast: true,
        successMessage: 'Research saved successfully!',
        onSuccess: () => {
          setShowSaveModal(false);
          setSaveTitle('');
          setSaveTags('');
        },
      }
    );
  }, [execute, results, saveTitle, query, summary, citations, saveTags]);

  const handleExport = useCallback(async (format: string) => {
    if (!results) return;

    await execute(
      () => researchAPI.exportResearch({
        research_id: Date.now().toString(),
        format,
        query,
        results,
        summary,
      }),
      {
        onSuccess: (response) => {
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
        },
        showSuccessToast: true,
        successMessage: `Exported as ${format.toUpperCase()}`,
      }
    );
  }, [execute, results, query, summary]);

  const handleCopyToClipboard = useCallback(async (text: string) => {
    try {
      await copyToClipboard(text);
      toast.success('Copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy to clipboard');
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults(null);
    setSummary('');
    setCitations([]);
    setSearchDuration(null);
    setValue('query', '');
  }, [setValue]);

  const handleSelectFromHistory = useCallback((query: string) => {
    setValue('query', query);
    setShowHistoryModal(false);
  }, [setValue]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <Sparkles className="h-8 w-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">
              AI Research Assistant
            </h1>
          </div>
          <p className="text-gray-600 mt-1">
            Conduct intelligent research with AI-powered web search
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            icon={History}
            onClick={() => setShowHistoryModal(true)}
            className="text-gray-500 hover:text-gray-700"
          >
            History
          </Button>
          {user && (
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {user.searches_used_this_month}/{user.searches_limit}
              </div>
              <div className="text-xs text-gray-500">searches used</div>
            </div>
          )}
        </div>
      </div>

      {/* Research Form */}
      <Card>
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
                className="w-full px-3 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={15}>15 results</option>
                <option value={20}>20 results</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              type="submit"
              loading={isLoading}
              icon={Search}
              className="flex-1"
            >
              {isLoading ? 'Researching...' : 'Start Research'}
            </Button>
            
            {results && (
              <Button
                type="button"
                variant="secondary"
                onClick={clearResults}
              >
                Clear
              </Button>
            )}
          </div>
        </form>
      </Card>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Research Stats */}
          {(results || searchDuration) && (
            <Card className="bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  {results && (
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-5 w-5 text-primary-600" />
                      <div>
                        <div className="text-lg font-semibold text-primary-900">
                          {results.length}
                        </div>
                        <div className="text-sm text-primary-700">Results found</div>
                      </div>
                    </div>
                  )}
                  {searchDuration && (
                    <div className="flex items-center space-x-2">
                      <Clock className="h-5 w-5 text-primary-600" />
                      <div>
                        <div className="text-lg font-semibold text-primary-900">
                          {(searchDuration / 1000).toFixed(1)}s
                        </div>
                        <div className="text-sm text-primary-700">Search time</div>
                      </div>
                    </div>
                  )}
                </div>
                {summary && (
                  <div className="text-sm text-primary-700">
                    ✨ AI Summary available
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Summary */}
          {summary && (
            <Card>
              <div className="flex items-center space-x-2 mb-4">
                <Sparkles className="h-5 w-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  AI Summary
                </h3>
              </div>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed">{summary}</p>
              </div>
            </Card>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={() => setShowSaveModal(true)}
              variant="secondary"
              icon={Save}
            >
              Save Research
            </Button>
            <Button
              onClick={() => handleExport('pdf')}
              variant="secondary"
              icon={Download}
              loading={isLoading}
            >
              Export PDF
            </Button>
            <Button
              onClick={() => handleExport('markdown')}
              variant="secondary"
              icon={Download}
              loading={isLoading}
            >
              Export Markdown
            </Button>
          </div>

          {/* Citations */}
          {citations.length > 0 && (
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Citations ({citations.length})
              </h3>
              <div className="space-y-2">
                {citations.map((citation, index) => (
                  <div
                    key={index}
                    className="flex items-start justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <span className="text-sm text-gray-700 flex-1">{citation}</span>
                    <Button
                      onClick={() => handleCopyToClipboard(citation)}
                      variant="ghost"
                      size="sm"
                      icon={Copy}
                      className="ml-2 text-gray-400 hover:text-gray-600"
                    >
                      <span className="sr-only">Copy citation</span>
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Search Results */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Search Results ({results.length})
              </h3>
              <Button
                variant="ghost"
                size="sm"
                icon={Filter}
                className="text-gray-500"
              >
                Filter
              </Button>
            </div>
            <div className="space-y-4">
              {results.map((result, index) => (
                <Card
                  key={index}
                  padding="md"
                  hover
                  className="border border-gray-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-2 hover:text-primary-600 transition-colors">
                        {result.title}
                      </h4>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                        {result.content}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center text-xs text-gray-500 space-x-4">
                          <span>Source: {result.source}</span>
                          {result.relevance_score && (
                            <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full">
                              {Math.round(result.relevance_score * 100)}% relevant
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCopyToClipboard(result.url)}
                            icon={Copy}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <span className="sr-only">Copy URL</span>
                          </Button>
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 hover:text-primary-700 p-1"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Save Research Modal */}
      <Modal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        title="Save Research"
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="Title"
            value={saveTitle}
            onChange={(e) => setSaveTitle(e.target.value)}
            placeholder="Enter a title for your research"
            icon={BookOpen}
          />
          
          <Input
            label="Tags (comma-separated)"
            value={saveTags}
            onChange={(e) => setSaveTags(e.target.value)}
            placeholder="research, ai, technology"
            helperText="Add tags to help organize your research"
          />

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              variant="secondary"
              onClick={() => setShowSaveModal(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={isLoading}
              icon={Save}
            >
              Save Research
            </Button>
          </div>
        </div>
      </Modal>

      {/* Search History Modal */}
      <Modal
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
        title="Search History"
        size="lg"
      >
        <SearchHistory
          ref={searchHistoryRef}
          onSelectQuery={handleSelectFromHistory}
        />
      </Modal>
    </div>
  );
};

export default Research;
