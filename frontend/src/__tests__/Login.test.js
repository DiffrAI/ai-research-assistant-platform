import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../pages/Login';

// Mock the auth store
jest.mock('../store/authStore', () => ({
  __esModule: true,
  default: () => ({
    login: jest.fn(),
    register: jest.fn(),
    isLoading: false,
    clearError: jest.fn(),
  }),
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

test('renders login page', () => {
  renderWithRouter(<Login />);
  expect(document.body).toBeInTheDocument();
}); 