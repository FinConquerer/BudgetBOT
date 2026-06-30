/** Dialog có thương hiệu: dùng thay cho Dialog trần. Header nền subtle + nút X, Fade (tắt khi reduced-motion). */
import { forwardRef, useId } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  IconButton,
  Typography,
  Fade,
} from "@mui/material";
import { XMarkIcon } from "@heroicons/react/24/outline";
import useReducedMotion from "../hooks/useReducedMotion.js";

const FadeTransition = forwardRef(function FadeTransition(props, ref) {
  return <Fade ref={ref} {...props} />;
});

/**
 * @param {{
 *   open:boolean, onClose:()=>void, title:string, description?:string,
 *   actions?:React.ReactNode, maxWidth?:string, children:React.ReactNode
 * }} props
 */
export default function BrandDialog({
  open,
  onClose,
  title,
  description,
  actions,
  maxWidth = "sm",
  children,
  ...rest
}) {
  const reduced = useReducedMotion();
  const titleId = useId();
  const descId = useId();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth={maxWidth}
      TransitionComponent={FadeTransition}
      transitionDuration={reduced ? 0 : 250}
      aria-labelledby={titleId}
      aria-describedby={description ? descId : undefined}
      {...rest}
    >
      <DialogTitle id={titleId} sx={{ bgcolor: "background.subtle", pr: 6 }}>
        {title}
        <IconButton
          onClick={onClose}
          sx={{ position: "absolute", right: 8, top: 8 }}
          aria-label="close"
        >
          <XMarkIcon style={{ width: 20, height: 20 }} />
        </IconButton>
      </DialogTitle>
      <DialogContent sx={{ pt: 2.5 }}>
        {description && (
          <Typography id={descId} variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {description}
          </Typography>
        )}
        <Box sx={{ pt: 1 }}>{children}</Box>
      </DialogContent>
      {actions && <DialogActions>{actions}</DialogActions>}
    </Dialog>
  );
}
