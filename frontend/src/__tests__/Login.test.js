/* eslint-env jest */
import { render, screen, fireEvent, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Login from '../pages/Login';
import useAuthStore from '../store/authStore';
import toast from 'react-hot-toast';

// Mock the auth store and react-hot-toast
jest.mock('../store/authStore');
jest.mock('react-hot-toast');

const renderWithRouter = (component) => {
  return render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      {component}
    </MemoryRouter>
  );
};

describe('Login page', () => {
  beforeEach(() => {
    useAuthStore.mockReturnValue({
      login: jest.fn(),
      register: jest.fn(),
      isLoading: false,
      clearError: jest.fn(),
      error: null,
    });
    toast.success = jest.fn();
    toast.error = jest.fn();
  });

  test('renders login page with email and password fields', () => {
    renderWithRouter(<Login />);

    // Check for email and password fields by placeholder text
    expect(screen.getByPlaceholderText('Email address')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
  });

  test('shows an error message on failed login', async () => {
    const login = jest.fn().mockResolvedValue({ success: false, error: 'Invalid credentials' });
    useAuthStore.mockReturnValue({ ...useAuthStore(), login });

    renderWithRouter(<Login />);

    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText('Email address'), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'wrongpassword' } });
      fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    });

    expect(toast.error).toHaveBeenCalledWith('Invalid credentials');
  });

  test('calls the login function and shows a success message on successful login', async () => {
    const login = jest.fn().mockResolvedValue({ success: true });
    useAuthStore.mockReturnValue({ ...useAuthStore(), login });

    renderWithRouter(<Login />);

    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText('Email address'), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
      fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    });

    expect(login).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password' });
    expect(toast.success).toHaveBeenCalledWith('Login successful!');
  });
});
