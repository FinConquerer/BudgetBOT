/** Hộp thoại xác nhận (xây trên BrandDialog). Nút xác nhận màu error, có trạng thái confirming. */
import { Button } from "@mui/material";
import { useTranslation } from "react-i18next";
import BrandDialog from "./BrandDialog.jsx";

/**
 * @param {{
 *   open:boolean, onClose:()=>void, onConfirm:()=>void,
 *   title:string, description?:string, confirming?:boolean, confirmLabel?:string
 * }} props
 */
export default function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirming = false,
  confirmLabel,
}) {
  const { t } = useTranslation();
  return (
    <BrandDialog
      open={open}
      onClose={onClose}
      title={title}
      description={description}
      maxWidth="xs"
      actions={
        <>
          <Button onClick={onClose} className="no-hover-lift">
            {t("common.cancel")}
          </Button>
          <Button variant="contained" color="error" onClick={onConfirm} disabled={confirming}>
            {confirmLabel || t("common.delete")}
          </Button>
        </>
      }
    >
      {null}
    </BrandDialog>
  );
}
