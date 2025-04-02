import React from "react"

const Button = React.forwardRef(({ 
    className = "", 
    variant = "default", 
    size = "default", 
    children,
    ...props 
}, ref) => {
    const variantClasses = {
        default: "bg-blue-600 text-white hover:bg-blue-700",
        outline: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50",
        ghost: "bg-transparent hover:bg-slate-100 text-slate-700",
    }
    
    const sizeClasses = {
        default: "h-10 px-4 py-2",
        sm: "h-8 px-3 text-sm",
        lg: "h-12 px-6",
        icon: "h-9 w-9",
    }
    
    const baseClasses = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none"

    return (
        <button
            className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
            ref={ref}
            {...props}
        >
            {children}
        </button>
    )
})

Button.displayName = "Button"

export { Button }
