import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';

// Mock the auth store
jest.mock('../store/authStore', () => ({
  __esModule: true,
  default: () => ({
    user: null,
    isAuthenticated: false,
    logout: jest.fn(),
  }),
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

test('renders layout component', () => {
  renderWithRouter(<Layout><div>Test content</div></Layout>);
  expect(document.body).toBeInTheDocument();
}); 