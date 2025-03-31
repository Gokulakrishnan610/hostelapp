import { Grid, GridProps } from '@mui/material';
import { ElementType } from 'react';

export interface StyledGridProps extends GridProps {
  item?: boolean;
  container?: boolean;
  xs?: number | boolean;
  sm?: number | boolean;
  md?: number | boolean;
  lg?: number | boolean;
  xl?: number | boolean;
  spacing?: number;
  component?: ElementType;
}

export const StyledGrid = ({ children, ...props }: StyledGridProps) => {
  return <Grid {...props}>{children}</Grid>;
}; 