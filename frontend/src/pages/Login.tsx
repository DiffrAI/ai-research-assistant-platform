import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Eye, EyeOff, Mail, Lock, User, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import useAuthStore from '../store/authStore';
import { Button, Input } from '../components/ui';
import { LoginCredentials, RegisterData } from '../types';

interface FormData extends RegisterData {
  // RegisterData already includes email, password, full_name
}

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isRegistering, setIsRegistering] = useState<boolean>(false);
  const { login, register, isLoading, clearError } = useAuthStore();
  const navigate = useNavigate();

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    clearError();

    if (isRegistering) {
      const result = await register(data);
      if (result.success) {
        toast.success('Registration successful! Please log in.');
        setIsRegistering(false);
        reset();
      } else {
        toast.error(result.error || 'Registration failed');
      }
    } else {
      // Only send email and password for login
      const loginData: LoginCredentials = { 
        email: data.email, 
        password: data.password 
      };
      const result = await login(loginData);
      if (result.success) {
        toast.success('Login successful!');
        navigate('/');
      } else {
        toast.error(result.error || 'Login failed');
      }
    }
  };

  // Reset form fields when switching between register and login
  useEffect(() => {
    reset();
  }, [isRegistering, reset]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
            <Search className="h-6 w-6 text-primary-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isRegistering ? 'Create your account' : 'Sign in to your account'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {isRegistering ? (
              <>
                Already have an account?{' '}
                <button
                  onClick={() => setIsRegistering(false)}
                  className="font-medium text-primary-600 hover:text-primary-500"
                >
                  Sign in
                </button>
              </>
            ) : (
              <>
                Don&apos;t have an account?{' '}
                <button
                  onClick={() => setIsRegistering(true)}
                  className="font-medium text-primary-600 hover:text-primary-500"
                >
                  Sign up
                </button>
              </>
            )}
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            {isRegistering && (
              <Input
                {...registerField('full_name', {
                  required: isRegistering ? 'Full name is required' : false,
                })}
                type="text"
                placeholder="Full Name"
                icon={User}
                error={errors.full_name?.message}
              />
            )}
            
            <Input
              {...registerField('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
              })}
              type="email"
              placeholder="Email address"
              icon={Mail}
              error={errors.email?.message}
            />
            
            <div className="relative">
              <Input
                {...registerField('password', {
                  required: 'Password is required',
                  minLength: {
                    value: 8,
                    message: 'Password must be at least 8 characters',
                  },
                })}
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                icon={Lock}
                error={errors.password?.message}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          <div>
            <Button
              type="submit"
              loading={isLoading}
              className="w-full"
            >
              {isRegistering ? 'Create Account' : 'Sign in'}
            </Button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              By signing in, you agree to our{' '}
              <a
                href="#"
                className="font-medium text-primary-600 hover:text-primary-500"
              >
                Terms of Service
              </a>{' '}
              and{' '}
              <a
                href="#"
                className="font-medium text-primary-600 hover:text-primary-500"
              >
                Privacy Policy
              </a>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
