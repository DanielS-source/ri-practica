import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VjsComponent } from './vjs.component';

describe('VjsComponent', () => {
  let component: VjsComponent;
  let fixture: ComponentFixture<VjsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [VjsComponent]
    });
    fixture = TestBed.createComponent(VjsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
