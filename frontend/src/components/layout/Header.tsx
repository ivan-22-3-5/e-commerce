"use client";

import React from 'react';
import Button from "@/components/ui/Button";

function Header() {
  return (
    <div className="flex flex-row items-center justify-between h-12 px-3">
      <div className="flex flex-row text-2xl font-bold">
        <h1 className="text-primary-light dark:text-primary-dark">Pet's</h1>
        <h1 className="text-amber-300">Love</h1>
      </div>
      <div className="flex flex-row gap-2">
        <Button variant="outlined" className='h-8 w-24'>Login</Button>
        <Button className='h-8 w-24'>Sign up</Button>
      </div>
    </div>
  );
}

export default Header;