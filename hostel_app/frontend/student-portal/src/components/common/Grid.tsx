import { Grid as MuiGrid, GridProps } from '@mui/material';
import { ElementType } from 'react';

export const Grid = ({ children, ...props }: GridProps) => {
  return <MuiGrid {...props}>{children}</MuiGrid>;
};

// Helper type for Grid items
export type GridItemProps = GridProps & {
  component?: ElementType;
}; 