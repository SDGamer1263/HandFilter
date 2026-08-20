"""User-facing error dialogs using tkinter."""
import tkinter as tk
from tkinter import messagebox
import sys
import traceback
import os


def show_model_error(detail: str = "") -> None:
    """Show error dialog for MediaPipe model initialization failure."""
    root = tk.Tk()
    root.withdraw()
    msg = (
        "HandFilter couldn't load the hand tracking model.\n\n"
        "This usually means the model file is missing or corrupted.\n\n"
        f"Details: {detail}\n\n"
        "Try reinstalling HandFilter. If the problem persists, "
        "please report this issue on GitHub."
    )
    messagebox.showerror("HandFilter - Model Error", msg)
    root.destroy()
    sys.exit(1)


def show_camera_error(retry_callback=None) -> bool:
    """
    Show error dialog for camera initialization failure.
    Returns True if user clicked Retry, False if Close.
    """
    root = tk.Tk()
    root.withdraw()

    msg = (
        "HandFilter couldn't access your camera.\n\n"
        "Check that:\n"
        "• Your camera is connected and powered on\n"
        "• Camera permissions are enabled in Windows Settings\n"
        "• Another application isn't using the camera\n\n"
        "Would you like to retry?"
    )

    result = messagebox.askretrycancel("HandFilter - Camera Unavailable", msg)
    root.destroy()
    return result


def show_generic_error(title: str, message: str, detail: str = "") -> None:
    """Show generic error dialog with optional detail."""
    root = tk.Tk()
    root.withdraw()
    full_msg = message
    if detail:
        full_msg += f"\n\nDetails: {detail}"
    full_msg += "\n\nHandFilter will now close."
    messagebox.showerror(f"HandFilter - {title}", full_msg)
    root.destroy()
    sys.exit(1)


def show_update_available(current_version: str, new_version: str, release_url: str) -> bool:
    """Show update available dialog. Returns True if user wants to update."""
    root = tk.Tk()
    root.withdraw()
    msg = (
        f"HandFilter {new_version} is available!\n"
        f"You are running {current_version}.\n\n"
        "Would you like to download and install the update now?"
    )
    result = messagebox.askyesno("HandFilter - Update Available", msg)
    root.destroy()
    return result


def show_update_downloaded(version: str) -> None:
    """Show notification that update was downloaded and will install on restart."""
    root = tk.Tk()
    root.withdraw()
    msg = (
        f"HandFilter {version} has been downloaded.\n\n"
        "The update will be installed the next time you start HandFilter."
    )
    messagebox.showinfo("HandFilter - Update Ready", msg)
    root.destroy()


def show_network_error(context: str = "check for updates") -> None:
    """Show non-blocking network error (doesn't exit app)."""
    root = tk.Tk()
    root.withdraw()
    msg = (
        f"Couldn't {context}.\n\n"
        "HandFilter will continue normally.\n"
        "Please check your internet connection and try again later."
    )
    messagebox.showwarning("HandFilter - Network Error", msg)
    root.destroy()


def exception_hook(exc_type, exc_value, exc_tb):
    """Global exception handler for unhandled exceptions."""
    detail = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(detail, file=sys.stderr)
    show_generic_error("Unexpected Error", "An unexpected error occurred.", detail[:500])


# Install global exception hook
sys.excepthook = exception_hook