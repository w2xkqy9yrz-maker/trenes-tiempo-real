// Notification display/click handler only. No cache, polling, or push subscription.
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('notificationclick',event=>{
  event.notification.close();
  const target=new URL('./#notificaciones',self.registration.scope).href;
  event.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(async clients=>{
    const page=clients.find(c=>c.url.startsWith(self.registration.scope));
    if(page){await page.navigate(target);return page.focus();}
    return self.clients.openWindow(target);
  }));
});
