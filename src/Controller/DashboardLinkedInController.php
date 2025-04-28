<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class DashboardLinkedInController extends AbstractController
{
    #[Route('/dashboard/linked/in', name: 'app_dashboard_linked_in')]
    public function index(): Response
    {
        $user = $this->getUser();
        return $this->render('dashboard_linked_in/index.html.twig', [
            'username' => $user->getUsername()
        ]);
    }
}
