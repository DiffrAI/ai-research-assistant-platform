import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import { UseApiOptions, UseApiReturn } from '../types';

export const useApi = (): UseApiReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (apiCall: () => Promise<any>, options: UseApiOptions = {}) => {
    const {
      onSuccess,
      onError,
      showSuccessToast = false,
      showErrorToast = true,
      successMessage = 'Operation completed successfully',
    } = options;

    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      
      if (showSuccessToast) {
        toast.success(successMessage);
      }
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'An error occurred';
      setError(errorMessage);
      
      if (showErrorToast) {
        toast.error(errorMessage);
      }
      
      if (onError) {
        onError(err);
      }
      
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return { loading, error, execute, reset };
};

interface UsePaginatedApiParams {
  [key: string]: any;
  page?: number;
  limit?: number;
}

interface UsePaginatedApiReturn<T> {
  data: T[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  loadMore: () => Promise<void>;
  refresh: () => void;
}

export const usePaginatedApi = <T>(
  apiCall: (params: UsePaginatedApiParams) => Promise<any>,
  initialParams: UsePaginatedApiParams = {}
): UsePaginatedApiReturn<T> => {
  const [data, setData] = useState<T[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const { loading, error, execute } = useApi();

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    try {
      const result = await execute(() => 
        apiCall({ ...initialParams, page, limit: 10 })
      );
      
      const newData = result.data?.data || [];
      setData(prev => page === 1 ? newData : [...prev, ...newData]);
      setHasMore(newData.length === 10);
      setPage(prev => prev + 1);
    } catch (err) {
      // Error handled by useApi
    }
  }, [apiCall, execute, hasMore, initialParams, loading, page]);

  const refresh = useCallback(() => {
    setData([]);
    setPage(1);
    setHasMore(true);
    loadMore();
  }, [loadMore]);

  return { data, loading, error, hasMore, loadMore, refresh };
};