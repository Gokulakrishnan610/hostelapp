import React from 'react';
import { Alert } from '@mui/material';

interface ErrorState {
  hasError: boolean;
  error: string;
}

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorState> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: '' };
  }

  static getDerivedStateFromError(error: Error) {
    return {
      hasError: true,
      error: error.message
    };
  }

  render() {
    if (this.state.hasError) {
      return <Alert severity="error">{this.state.error}</Alert>;
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 