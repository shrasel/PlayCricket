/**
 * Role Guard
 * 
 * Protects routes based on user roles.
 * Checks if user has required roles specified in route data.
 * 
 * Usage in routes:
 * {
 *   path: 'admin',
 *   component: AdminComponent,
 *   canActivate: [AuthGuard, RoleGuard],
 *   data: { roles: ['ADMIN'] }
 * }
 */

import { Injectable } from '@angular/core';
import { Router, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    // Get required roles from route data
    const requiredRoles = route.data['roles'] as string[] | undefined;
    
    // If no roles specified, allow access
    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }
    
    return this.authService.currentUser$.pipe(
      take(1),
      map(user => {
        if (!user) {
          // Not authenticated, redirect to login
          return this.router.createUrlTree(['/login']);
        }
        
        // Check if user has any of the required roles
        const hasRequiredRole = requiredRoles.some(role => 
          user.roles.includes(role)
        );
        
        if (hasRequiredRole) {
          return true;
        }
        
        // User doesn't have required role, redirect to access denied
        return this.router.createUrlTree(['/access-denied']);
      })
    );
  }

  canActivateChild(
    childRoute: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return this.canActivate(childRoute, state);
  }
}
